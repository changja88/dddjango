"""Same frozen oracle, adapted to Claude's panel-B/preview-A/note-A ownership design."""
import argparse
from collections import Counter
import json
import platform
import re
import subprocess
import traceback

from playwright.sync_api import expect, sync_playwright
from browser_support import ROOT, PYTHON, CHROME, RESOURCE_TRACKER, Evidence, django_server, local_image

# This delays dispatch to an app load handler after an actual native image load, never
# fabricates a load/error or an HTTP swap. It is not a claim about browser task ordering.
LOAD_HOLD = '''(() => {
  const add = document.addEventListener.bind(document);
  window.__holdImageHandler = false;
  window.__heldImageCallbacks = [];
  document.addEventListener = function(type, listener, options) {
    if (type !== 'load') return add(type, listener, options);
    return add(type, function(event) {
      if (window.__holdImageHandler && event.target instanceof HTMLImageElement && event.target.matches('[data-image-preview-output]')) {
        window.__heldImageCallbacks.push(() => listener.call(this, event));
        return;
      }
      return listener.call(this, event);
    }, options);
  };
})();'''

def run(label):
    lane='claude';ev=Evidence(lane,label);current='I12'
    result=subprocess.run([PYTHON,'manage.py','check'],cwd=ROOT/lane/'app',capture_output=True,text=True)
    ev.data['django_check']={'exit_code':result.returncode,'output':result.stdout+result.stderr};ev.save();assert result.returncode==0
    with django_server(lane,18751,label) as base,sync_playwright() as pw:
        try: browser=pw.chromium.launch(executable_path=CHROME,headless=True)
        except Exception as error:
            ev.data.update(status='ENVIRONMENT_FAILURE',launch_error=str(error));ev.save();raise
        context=browser.new_context(viewport={'width':1280,'height':1000});context.add_init_script(RESOURCE_TRACKER);context.add_init_script(LOAD_HOLD)
        page=context.new_page();ev.attach(page);ev.data['browser_version']=browser.version
        def root(key):return page.locator('#ui-lab-preview-'+key)
        def panel(key):return page.locator('#ui-lab-panel-'+key)
        def field(kind,key='a'):
            names={'file':'input','clear':'clear','image':'output','filename':'name','error':'error'}
            return root(key).locator('[data-image-preview-'+names[kind]+']')
        def password(key='a'):return page.locator('#ui-lab-password-'+key+' [data-password-input]')
        def button(key='a'):return page.locator('#ui-lab-password-'+key+' [data-password-toggle]')
        def resources():return ev.resource_state(page)
        def choose(key,name):
            before=len(resources()['created']);field('file',key).set_input_files(local_image(name))
            expect(field('filename',key)).to_have_text(name);expect(field('image',key)).to_be_visible()
            expect(field('image',key)).to_have_js_property('complete',True)
            assert field('image',key).evaluate('(img)=>img.naturalWidth===2&&img.naturalHeight===2')
            assert len(resources()['created'])==before+1
            return field('image',key).get_attribute('src')
        def toggle(key='a',keyboard=None):
            before=len(resources()['typeAssignments']);old=password(key).get_attribute('type')
            if keyboard:button(key).focus();page.keyboard.press(keyboard)
            else:button(key).click()
            new='text' if old=='password' else 'password';expect(password(key)).to_have_attribute('type',new)
            expect(button(key)).to_have_attribute('aria-pressed',str(new=='text').lower())
            assert len(resources()['typeAssignments'])==before+1
        targets={'panel':'#ui-lab-panel-b','preview':'#ui-lab-preview-a','note':'#ui-lab-note-a'}
        def revision(target):
            value=target.get_attribute('data-revision') or target.get_attribute('data-revision-marker')
            if value:return value
            found=re.search(r'rev-[a-f0-9]+',target.inner_text());assert found,target.inner_text();return found.group()
        def swap(kind,keyboard=None):
            target=page.locator(targets[kind]);old=revision(target);before=page.evaluate('window.__htmxSettled.length')
            trigger=target.locator('[hx-target="'+targets[kind]+'"]')
            with page.expect_response(lambda r:r.request.headers.get('hx-request')=='true') as info:
                if keyboard:trigger.focus();page.keyboard.press(keyboard)
                else:trigger.click()
            response=info.value;assert response.status==200;body=response.text()
            assert not re.search(r'<script\b',body,re.I)
            page.wait_for_function('(n)=>window.__htmxSettled.length>n',arg=before)
            new=revision(page.locator(targets[kind]));assert new!=old and new in body
            ev.data['htmx_responses'].append({'kind':kind,'url':response.url,'status':response.status,'revision':new,'html':body})
            return new
        try:
            page.goto(base+'/lab/ui-lab/',wait_until='networkidle');expect(button()).to_be_visible()
            current='I1';password().fill('alpha-private');password('b').fill('beta-private');toggle()
            expect(password('b')).to_have_attribute('type','password');expect(password('b')).to_have_value('beta-private')
            assert button().get_attribute('aria-controls')==password().get_attribute('id');ev.passed('I1','Own password and accessible state change once; neighbor remains masked and unchanged.')
            current='I2';toggle(keyboard='Enter');toggle(keyboard='Space');toggle('b',keyboard='Enter');toggle('b');ev.passed('I2','Native Enter/Space and both password instances each change exactly once.')
            current='I3';first=choose('a','<img src=x onerror=alert(1)>.png');neighbor=choose('b','neighbor.png')
            assert field('filename').locator('*').count()==0 and field('image').get_attribute('src')==first;ev.passed('I3','Independent decoded images and literal markup filename, with no interpreted filename descendants.')
            current='I4';replacement=choose('a','replacement.png');assert resources()['revoked'].count(first)==1
            field('clear').click();assert resources()['revoked'].count(replacement)==1;expect(field('filename')).to_have_text('');expect(field('image')).not_to_be_visible()
            assert neighbor not in resources()['revoked'];ev.passed('I4','Reselect/clear revoke prior resources exactly once, retaining neighbor.')
            current='I5';previous=choose('a','before-invalid.png');before=len(resources()['created'])
            field('file').set_input_files({'name':'invalid.png','mimeType':'image/png','buffer':b'not a real image'})
            expect(field('filename')).to_have_text('');expect(field('image')).not_to_be_visible();expect(field('error')).to_be_visible()
            assert field('error').inner_text().strip();assert resources()['revoked'].count(previous)==1
            assert len(resources()['created'])==before+1 and resources()['created'][-1]['url'] in resources()['revoked']
            ev.passed('I5','Actual invalid PNG native error clears stale success and revokes failed/previous resources.')
            mime_previous=choose('a','before-mime.png');mime_before=len(resources()['created'])
            field('file').set_input_files({'name':'not-an-image.txt','mimeType':'text/plain','buffer':b'plain text MIME fixture'})
            expect(field('filename')).to_have_text('');expect(field('image')).not_to_be_visible();expect(field('error')).to_be_visible()
            assert len(resources()['created'])==mime_before and resources()['revoked'].count(mime_previous)==1
            ev.data['non_image_mime_probe']={'status':'PASS','mime':'text/plain','new_url_allocations':0,'prior_url':mime_previous,'prior_url_revocations':1,'stale_success_cleared':True}
            current='I8';retained=choose('a','retained.png');owner=root('a').element_handle();image_node=field('image').element_handle();swap('note',keyboard='Enter')
            assert owner.evaluate('(n)=>n.isConnected') and image_node.evaluate('(n)=>n.isConnected');assert retained not in resources()['revoked'];expect(field('filename')).to_have_text('retained.png')
            ev.passed('I8','Real note-child HTTP swap within retained preview owner preserves owner/image identities and live URL.')
            current='I9';retained_panel=panel('a').element_handle();swap('preview')
            assert retained_panel.evaluate('(n)=>n.isConnected') and not owner.evaluate('(n)=>n.isConnected');assert resources()['revoked'].count(retained)==1
            expect(password()).to_have_value('alpha-private');expect(password()).to_have_attribute('type','text');assert neighbor not in resources()['revoked']
            preserved_a=choose('a','preserved-a.png');old_b=root('b').element_handle();swap('panel')
            assert not old_b.evaluate('(n)=>n.isConnected') and resources()['revoked'].count(neighbor)==1;assert preserved_a not in resources()['revoked'];expect(field('filename')).to_have_text('preserved-a.png')
            ev.passed('I9','Preview-owner A replaced as dependent child of retained panel A; panel-B full-root replacement removes owner B. Opposite preview/password preserved. Does not claim a dependent-control replacement under the same preview owner.')
            current='I7'
            for iteration in range(3):
                a=choose('a',f'a-{iteration}.png');b=choose('b',f'b-{iteration}.png')
                swap('note');assert a not in resources()['revoked'] and b not in resources()['revoked']
                swap('preview');assert resources()['revoked'].count(a)==1 and b not in resources()['revoked'];expect(password()).to_have_value('alpha-private')
                fresh=choose('a',f'new-a-{iteration}.png');swap('panel');assert resources()['revoked'].count(b)==1 and fresh not in resources()['revoked']
                password('b').fill('new-b');toggle('b');expect(password()).to_have_attribute('type','text')
                choose('b',f'new-b-{iteration}.png')
            ev.passed('I7','Three additional real note/preview-owner/full-panel cycles; new controls work with one effect and retained neighbor state preserved.')
            # Delay callback delivery after actual native load to cover owner removal and independent child.
            pending=[]
            for kind,key in [('note','a'),('preview','a'),('panel','b')]:
                page.evaluate('window.__holdImageHandler=true;window.__heldImageCallbacks=[]')
                field('file',key).set_input_files(local_image('pending-'+kind+'.png'))
                page.wait_for_function('window.__heldImageCallbacks.length>0');url=resources()['created'][-1]['url']
                marker=swap(kind)
                page.evaluate('window.__holdImageHandler=false')
                if kind=='note':
                    assert url not in resources()['revoked']
                    page.evaluate('window.__heldImageCallbacks.splice(0).forEach(callback=>callback())')
                    expect(field('filename',key)).to_have_text('pending-note.png');expect(field('image',key)).to_be_visible()
                else:
                    assert resources()['revoked'].count(url)==1;new=choose(key,'after-pending-'+kind+'.png')
                    page.evaluate('window.__heldImageCallbacks.splice(0).forEach(callback=>callback())')
                    assert field('image',key).get_attribute('src')==new and new not in resources()['revoked'];expect(field('filename',key)).to_have_text('after-pending-'+kind+'.png')
                pending.append({'kind':kind,'key':key,'revision':marker,'url':url,'status':'PASS'})
            ev.data['delayed_load_handler_probe']={'injection':'Native image load occurs first; harness defers only app handler delivery while actual HTTP swap executes. No fabricated event or claim about browser task ordering.','results':pending}
            failure_url=base+'/lab/ui-lab/fragment/panel/';old_revision=revision(panel('b'));old_url=field('image','b').get_attribute('src');console_before=len(ev.data['console_errors'])
            page.route(failure_url,lambda route:route.fulfill(status=503,content_type='text/plain',body='labelled harness HTTP failure'),times=1)
            trigger=panel('b').locator('[hx-target="#ui-lab-panel-b"]')
            with page.expect_response(lambda r:r.url==failure_url and r.status==503):
                trigger.focus();page.keyboard.press('Enter')
            assert revision(panel('b'))==old_revision and field('image','b').get_attribute('src')==old_url and old_url not in resources()['revoked'];expect(trigger).to_be_focused()
            retry_revision=swap('panel',keyboard='Enter');assert resources()['revoked'].count(old_url)==1
            expected_errors=ev.data['console_errors'][console_before:];assert all('503' in message for message in expected_errors),expected_errors
            ev.data['injected_http_failure']={'status':503,'retained_revision':old_revision,'retained_url':old_url,'retry_revision':retry_revision,'retry_status':200,'expected_console_errors':expected_errors};del ev.data['console_errors'][console_before:]
            ev.passed('I6',f"Recorded {len(ev.data['htmx_responses'])} actual HTTP200 fragment responses with changed server revision markers.")
            current='I11';counts=Counter(r['url'] for r in ev.data['requests'] if r['type']=='script');assert len(counts)==3 and all(n==1 for n in counts.values());assert page.locator('script[src]').count()==3
            ev.data['script_network_counts']=dict(counts);ev.passed('I11','Core and both features each loaded once; all returned actual fragment HTML has no scripts.')
            current='I10';native=context.new_page();disabled=[]
            def disable(route):disabled.append(route.request.url);route.fulfill(status=200,content_type='application/javascript',body='/* labelled feature disable */')
            native.route('**/static/web/js/*.js',disable);native.goto(base+'/lab/ui-lab/',wait_until='networkidle');details=native.locator('details');assert details.count()==1 and len(disabled)==2
            details.locator('summary').focus();native.keyboard.press('Enter');expect(details).to_have_attribute('open','');native.keyboard.press('Space');expect(details).not_to_have_attribute('open','');native.close()
            ev.data['disabled_feature_requests']=disabled;ev.passed('I10','Both feature scripts replaced by empty responses; native disclosure works via Enter/Space.')
            current='I12';assert not ev.data['console_errors'],ev.data['console_errors'];assert not ev.data['page_errors'],ev.data['page_errors'];ev.passed('I12','Django check exit0 and actual browser console/pageerrors empty.')
            ev.data['resources']=resources();ev.data['runtime']={'os':platform.platform(),'python':platform.python_version(),'viewport':page.viewport_size}
            ev.data['rendered_style']=page.locator('body').evaluate('(node)=>({font:getComputedStyle(node).fontFamily,lineHeight:getComputedStyle(node).lineHeight})')
            page.screenshot(path=str(ROOT/lane/(label+'.png')),full_page=True)
            page.set_viewport_size({'width':375,'height':812});ev.data['narrow_viewport']={'viewport':page.viewport_size,'scroll_width':page.evaluate('document.documentElement.scrollWidth'),'inner_width':page.evaluate('window.innerWidth')}
            page.screenshot(path=str(ROOT/lane/(label+'-narrow.png')),full_page=True);ev.data['status']='PASS'
        except Exception as error:
            ev.failed(current,error);ev.data.update(status='FAIL',traceback=traceback.format_exc(),resources=resources());page.screenshot(path=str(ROOT/lane/(label+'-failure.png')),full_page=True);raise
        finally:ev.save();browser.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('label');run(parser.parse_args().label)
