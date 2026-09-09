"""Frozen behavioral oracle evaluated independently against generated Django UI."""
import argparse
from collections import Counter
import json
import platform
from pathlib import Path
import re
import subprocess
import traceback

from playwright.sync_api import sync_playwright, expect
from browser_support import ROOT, PYTHON, CHROME, RESOURCE_TRACKER, Evidence, django_server, local_image

def run(lane, label):
    config = json.loads((ROOT / lane / 'browser-selectors.json').read_text())
    evidence = Evidence(lane, label)
    current = 'I12'
    check = subprocess.run([PYTHON, 'manage.py', 'check'], cwd=ROOT/lane/'app', capture_output=True, text=True)
    evidence.data['django_check'] = {'exit_code': check.returncode, 'output': check.stdout + check.stderr}
    evidence.save()
    assert check.returncode == 0
    with django_server(lane, 18751 if lane == 'claude' else 18752, label) as base, sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(executable_path=CHROME, headless=True)
        except Exception as error:
            evidence.data['status']='ENVIRONMENT_FAILURE'
            evidence.data['launch_error']=str(error)
            evidence.save()
            raise
        evidence.data['browser_version'] = browser.version
        context = browser.new_context(viewport={'width': 1280, 'height': 1000})
        context.add_init_script(RESOURCE_TRACKER)
        page = context.new_page()
        evidence.attach(page)
        def locator(kind, key='a'):
            return page.locator(config[kind].format(k=key))
        def resource():
            return evidence.resource_state(page)
        def select(key, name, rgb=(220,40,60)):
            before = len(resource()['created'])
            locator('file', key).set_input_files(local_image(name,rgb))
            expect(locator('filename',key)).to_have_text(name)
            expect(locator('image',key)).to_be_visible()
            assert locator('image',key).evaluate('(img) => img.complete && img.naturalWidth === 2 && img.naturalHeight === 2')
            assert len(resource()['created']) == before + 1, 'A single selection must allocate one owned URL'
            return locator('image',key).get_attribute('src')
        def toggle(key='a', keyboard=None):
            before = len(resource()['typeAssignments'])
            old = locator('password',key).get_attribute('type')
            if keyboard:
                locator('toggle',key).focus()
                page.keyboard.press(keyboard)
            else:
                locator('toggle',key).click()
            new = 'text' if old == 'password' else 'password'
            expect(locator('password',key)).to_have_attribute('type',new)
            assert len(resource()['typeAssignments']) == before + 1, 'A single activation must change type exactly once'
            if locator('toggle',key).get_attribute('aria-pressed') is not None:
                expect(locator('toggle',key)).to_have_attribute('aria-pressed',str(new=='text').lower())
            else:
                assert locator('toggle',key).get_attribute('aria-label') or locator('toggle',key).inner_text()
        def swap(kind, key='a', keyboard=None):
            target = locator(kind,key)
            old_revision = target.get_attribute('data-revision')
            settled_before = page.evaluate('window.__htmxSettled.length')
            assert old_revision
            with page.expect_response(lambda response: response.request.headers.get('hx-request') == 'true') as response_info:
                if keyboard:
                    locator('refresh_'+kind,key).focus()
                    page.keyboard.press(keyboard)
                else:
                    locator('refresh_'+kind,key).click()
            response = response_info.value
            assert response.status == 200
            body = response.text()
            assert not re.search(r'<script\b(?![^>]*type=["\']application/json)',body,re.I), 'Fragment contains executable script'
            expect(locator(kind,key)).not_to_have_attribute('data-revision',old_revision)
            revision = locator(kind,key).get_attribute('data-revision')
            assert revision and revision in body
            page.wait_for_function('(before) => window.__htmxSettled.length > before', arg=settled_before)
            evidence.data['htmx_responses'].append({'url':response.url,'status':response.status,'revision':revision,'html':body})
            return revision
        try:
            page.goto(base+config['path'],wait_until='networkidle')
            expect(locator('toggle')).to_be_visible()
            current='I1'
            locator('password').fill('alpha-private')
            locator('password','b').fill('beta-private')
            toggle()
            expect(locator('password','b')).to_have_attribute('type','password')
            expect(locator('password','b')).to_have_value('beta-private')
            assert locator('toggle').get_attribute('aria-controls') == locator('password').get_attribute('id')
            evidence.passed('I1','Own input visibility and accessible state changed once; neighbor remained masked with original value.')
            current='I2'
            toggle(keyboard='Enter')
            toggle(keyboard='Space')
            expect(locator('password','b')).to_have_attribute('type','password')
            evidence.passed('I2','Native Enter and Space each toggled exactly once.')
            current='I3'
            malicious_name='<img src=x onerror=alert(1)>.png'
            first=select('a',malicious_name)
            neighbor=select('b','neighbor.png',(30,100,220))
            expect(locator('filename')).to_have_text(malicious_name)
            assert locator('filename').locator('*').count()==0
            assert locator('image').get_attribute('src')==first
            evidence.passed('I3','Two decoded local 2x2 images, independent URLs, literal filename markup with no child elements.')
            current='I4'
            replacement=select('a','replacement.png',(20,200,60))
            assert resource()['revoked'].count(first)==1
            locator('clear').click()
            assert resource()['revoked'].count(replacement)==1
            expect(locator('image')).not_to_be_visible()
            expect(locator('filename')).to_have_text('')
            assert locator('image','b').get_attribute('src')==neighbor and neighbor not in resource()['revoked']
            evidence.passed('I4','Reselect and clear revoked each prior URL exactly once; neighbor retained.')
            current='I5'
            previous=select('a','before-invalid.png')
            before=len(resource()['created'])
            locator('file').set_input_files({'name':'broken.png','mimeType':'image/png','buffer':b'not an image; real decode failure'})
            expect(locator('filename')).to_have_text('')
            expect(locator('image')).not_to_be_visible()
            page.wait_for_function('() => window.__resourceEvidence.created.length > '+str(before)+' && window.__resourceEvidence.revoked.includes(window.__resourceEvidence.created.at(-1).url)')
            assert resource()['revoked'].count(previous)==1
            assert locator('status').inner_text().strip()
            evidence.data['invalid_decode_state']=locator('status').inner_text()
            evidence.passed('I5','Invalid PNG bytes caused an actual image decode failure, released failed/previous URLs, and removed stale success.')
            # Labelled timing injection delays completion after the browser truly decoded a PNG.
            page.evaluate('''() => {
              const original = HTMLImageElement.prototype.decode;
              let first = true;
              window.__heldReady = false;
              HTMLImageElement.prototype.decode = function() {
                const decoded = original.call(this);
                if (!first) return decoded;
                first = false;
                return decoded.then(() => new Promise(resolve => {
                  window.__releaseHeldDecode = resolve;
                  window.__heldReady = true;
                }));
              };
            }''')
            locator('file').set_input_files(local_image('delayed-old.png'))
            page.wait_for_function('window.__heldReady === true')
            delayed=resource()['created'][-1]['url']
            locator('clear').click()
            latest=select('a','latest-wins.png')
            page.evaluate('async () => { window.__releaseHeldDecode(); await Promise.resolve(); await Promise.resolve(); }')
            expect(locator('filename')).to_have_text('latest-wins.png')
            assert locator('image').get_attribute('src')==latest and latest not in resource()['revoked']
            assert resource()['revoked'].count(delayed)==1
            evidence.data['late_decode_probe']='PASS: labelled delay after real native decode, then clear/reselect; stale completion did not replace latest success or revoke its resource.'
            current='I8'
            retained=select('a','retained.png')
            owner=locator('owner').element_handle()
            body=locator('body').element_handle()
            swap('note')
            assert owner.evaluate('(node) => node.isConnected') and body.evaluate('(node) => node.isConnected')
            assert locator('image').get_attribute('src')==retained and retained not in resource()['revoked']
            expect(locator('filename')).to_have_text('retained.png')
            evidence.passed('I8','Real independent-child HTTP swap retained owner/body identities, displayed image and live URL.')
            current='I9'
            swap('body')
            assert owner.evaluate('(node) => node.isConnected') and not body.evaluate('(node) => node.isConnected')
            assert resource()['revoked'].count(retained)==1 and neighbor not in resource()['revoked']
            expect(locator('password')).to_have_value('alpha-private')
            expect(locator('password')).to_have_attribute('type','text')
            root_url=select('a','before-root.png')
            old_owner=locator('owner').element_handle()
            swap('panel')
            assert not old_owner.evaluate('(node) => node.isConnected')
            assert resource()['revoked'].count(root_url)==1 and neighbor not in resource()['revoked']
            expect(locator('password','b')).to_have_value('beta-private')
            assert locator('image','b').get_attribute('src')==neighbor
            evidence.passed('I9','Dependent-child removal released only its resource under retained owner; full-root HTTP replacement removed owner and released only its URL; neighbor remained usable.')
            current='I7'
            for i in range(3):
                locator('password').fill('cycle-'+str(i))
                toggle()
                allocated=select('a',f'body-cycle-{i}.png')
                swap('body')
                assert resource()['revoked'].count(allocated)==1
                expect(locator('password')).to_have_value('cycle-'+str(i))
                fresh=select('a',f'root-cycle-{i}.png')
                swap('panel')
                assert resource()['revoked'].count(fresh)==1
                expect(locator('password')).to_have_attribute('type','password')
                assert neighbor not in resource()['revoked']
            toggle(keyboard='Enter')
            select('a','final.png')
            evidence.passed('I7','Three additional real dependent-child/full-root cycles; new controls usable and each activation/allocation produced exactly one effect.')
            if lane == 'codex':
                # The generated design additionally specifies both directions and pending work at swaps.
                for key, other in [('a','b'),('b','a')]:
                    other_url=select(other,'retained-'+other+'.png')
                    other_password=locator('password',other).input_value()
                    other_type=locator('password',other).get_attribute('type')
                    for kind in ['note','body','panel']:
                        for iteration in range(3):
                            own_url=select(key,f'{key}-{kind}-{iteration}.png')
                            swap(kind,key,keyboard='Enter' if iteration==0 else None)
                            if iteration==0:
                                expect(locator('refresh_'+kind,key)).to_be_focused()
                            if kind=='note':
                                assert own_url not in resource()['revoked']
                                assert locator('image',key).get_attribute('src')==own_url
                            else:
                                assert resource()['revoked'].count(own_url)==1
                            assert other_url not in resource()['revoked']
                            assert locator('image',other).get_attribute('src')==other_url
                            expect(locator('password',other)).to_have_value(other_password)
                            expect(locator('password',other)).to_have_attribute('type',other_type)
                    toggle(key,keyboard='Space')
                    toggle(key)
                evidence.data['bidirectional_repetition']='PASS: A and B each received three note/body/panel HTTP swaps; retained opposite password/image preserved; keyboard refresh focus retained on all three scopes.'
                pending_results=[]
                for kind in ['note','body','panel']:
                    page.evaluate('''() => {
                      const original=HTMLImageElement.prototype.decode;
                      let first=true;
                      window.__heldReady=false;
                      HTMLImageElement.prototype.decode=function() {
                        const decoded=original.call(this);
                        if (!first) return decoded;
                        first=false;
                        return decoded.then(() => new Promise(resolve => {
                          window.__heldReady=true;
                          window.__releaseHeldDecode=resolve;
                        }));
                      };
                    }''')
                    locator('file').set_input_files(local_image('pending-'+kind+'.png'))
                    page.wait_for_function('window.__heldReady === true')
                    pending_url=resource()['created'][-1]['url']
                    revision=swap(kind)
                    if kind=='note':
                        assert pending_url not in resource()['revoked']
                        page.evaluate('async () => {window.__releaseHeldDecode(); await Promise.resolve(); await Promise.resolve();}')
                        expect(locator('filename')).to_have_text('pending-note.png')
                        assert locator('image').get_attribute('src')==pending_url
                    else:
                        assert resource()['revoked'].count(pending_url)==1
                        fresh_url=select('a','after-pending-'+kind+'.png')
                        page.evaluate('async () => {window.__releaseHeldDecode(); await Promise.resolve(); await Promise.resolve();}')
                        expect(locator('filename')).to_have_text('after-pending-'+kind+'.png')
                        assert locator('image').get_attribute('src')==fresh_url and fresh_url not in resource()['revoked']
                    pending_results.append({'kind':kind,'revision':revision,'pending_url':pending_url,'status':'PASS','injection':'Delayed fulfillment after real native PNG decode; actual HTTP swap before release.'})
                evidence.data['pending_decode_across_swap']=pending_results
                failure_url=base+'/lab/ui-lab/a/panel/'
                old_revision=locator('panel').get_attribute('data-revision')
                old_preview=locator('image').get_attribute('src')
                console_start=len(evidence.data['console_errors'])
                page.route(failure_url,lambda route: route.fulfill(status=503,content_type='text/plain',body='labelled harness HTTP failure'),times=1)
                with page.expect_response(lambda response:response.url==failure_url and response.status==503):
                    locator('refresh_panel').focus();page.keyboard.press('Enter')
                expect(locator('panel')).to_have_attribute('data-revision',old_revision)
                assert locator('image').get_attribute('src')==old_preview and old_preview not in resource()['revoked']
                expect(locator('refresh_panel')).to_be_focused()
                swap('panel',keyboard='Enter')
                injected_errors=evidence.data['console_errors'][console_start:]
                assert all('503' in message for message in injected_errors),injected_errors
                evidence.data['injected_http_failure']={'status':503,'retained_revision':old_revision,'retained_url':old_preview,'retry':'actual HTTP200 and changed revision','expected_console_errors':injected_errors}
                del evidence.data['console_errors'][console_start:]
            evidence.passed('I6',f"Captured {len(evidence.data['htmx_responses'])} actual outgoing HTMX requests with HTTP200 HTML and changed server revision markers.")
            current='I11'
            scripts=[r for r in evidence.data['requests'] if r['type']=='script']
            counts=Counter(r['url'] for r in scripts)
            assert len(counts)==3 and all(count==1 for count in counts.values()),counts
            assert len(page.locator('script[src]').all())==3
            evidence.data['script_network_counts']=dict(counts)
            evidence.passed('I11','Core plus two external feature scripts each fetched once per page; all actual fragment response HTML contains no executable script.')
            current='I10'
            native=context.new_page()
            blocked=[]
            def disable_features(route):
                blocked.append(route.request.url)
                route.fulfill(status=200,content_type='application/javascript',body='/* independent harness: custom feature disabled */')
            native.route('**/static/web/js/*.js',disable_features)
            native.goto(base+config['path'],wait_until='networkidle')
            details=native.locator('details')
            summary=details.locator('summary')
            assert details.count()==1 and len(blocked)==2
            expect(details).not_to_have_attribute('open','')
            summary.focus();native.keyboard.press('Enter')
            expect(details).to_have_attribute('open','')
            native.keyboard.press('Space');expect(details).not_to_have_attribute('open','')
            evidence.data['disabled_feature_requests']=blocked
            evidence.passed('I10','Both custom feature responses replaced with empty scripts by labelled harness injection; native disclosure opened/closed using keyboard.')
            native.close()
            current='I12'
            assert not evidence.data['page_errors'],evidence.data['page_errors']
            assert not evidence.data['console_errors'],evidence.data['console_errors']
            evidence.passed('I12','Actual Django system check exit0; primary browser console errors and pageerrors empty, including handled invalid decode.')
            evidence.data['resources']=resource()
            evidence.data['runtime']={'os':platform.platform(),'python':platform.python_version(),'viewport':page.viewport_size}
            page.screenshot(path=str(ROOT/lane/(label+'.png')),full_page=True)
            page.set_viewport_size({'width':375,'height':812})
            evidence.data['narrow_viewport']={'viewport':page.viewport_size,'scroll_width':page.evaluate('document.documentElement.scrollWidth'),'inner_width':page.evaluate('window.innerWidth')}
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Narrow viewport horizontally overflows'
            page.screenshot(path=str(ROOT/lane/(label+'-narrow.png')),full_page=True)
            evidence.data['status']='PASS'
        except Exception as error:
            evidence.failed(current,error)
            evidence.data['status']='FAIL'
            evidence.data['traceback']=traceback.format_exc()
            evidence.data['resources']=resource()
            page.screenshot(path=str(ROOT/lane/(label+'-failure.png')),full_page=True)
            raise
        finally:
            evidence.save()
            browser.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('lane',choices=['claude','codex'])
    parser.add_argument('label')
    args=parser.parse_args()
    run(args.lane,args.label)
