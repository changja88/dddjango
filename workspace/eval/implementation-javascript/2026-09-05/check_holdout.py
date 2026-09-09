import asyncio, json, sys
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).parent
async def run():
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
        page=await browser.new_page()
        results=[]; errors=[]; requests=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda r:requests.append({'url':r.url,'status':r.status}) if '/fragment/' in r.url else None)
        await page.add_init_script('''window.pendingCopies=[]; Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText(text){return new Promise((resolve,reject)=>pendingCopies.push({text,resolve,reject}));}}});''')
        await page.goto('http://127.0.0.1:8771/holdout/',wait_until='networkidle')
        async def record(id,ok,detail=''): results.append({'id':id,'pass':bool(ok),'detail':detail})
        async def start(root='a',text='text',key=False):
            await page.locator(f'#copy-{root} input').fill(text)
            button=page.locator(f'#copy-{root} button')
            if key: await button.focus(); await button.press('Enter')
            else: await button.click()
            return await page.evaluate('pendingCopies.length-1')
        async def finish(index,fail=False):
            await page.evaluate('''([i,fail])=>{ if(fail)pendingCopies[i].reject(new DOMException('denied','NotAllowedError'));else pendingCopies[i].resolve(); }''',[index,fail])
        async def status(root='a'): return await page.locator(f'#copy-{root} output').text_content()
        async def swap(kind,target,style='outerHTML'):
            await page.evaluate('([kind,target,swap])=>htmx.ajax("GET","/fragment/"+kind,{target,swap})',[kind,target,style])
            await page.wait_for_timeout(80)
        one=await start(text='first',key=True)
        await record('C1.pending',await status()=='')
        await finish(one); await record('C1.success.keyboard',await status()=='복사했습니다')
        two=await start(text='failure'); await finish(two,True); await record('C2.failure',await status()=='복사하지 못했습니다')
        old=await start(text='old'); new=await start(text='new'); await finish(new); await finish(old,True)
        await record('C3.latest',await status()=='복사했습니다')
        other=await start('b','independent'); await finish(other,True)
        await record('C4.isolation',await status('b')=='복사하지 못했습니다' and await status()=='복사했습니다')
        old=await start(text='removed-root'); await swap('copy-root','#copy-a'); await finish(old)
        await record('C5.root',await status()=='')
        old=await start(text='removed-input'); await swap('copy-input','#copy-a input'); await finish(old)
        await record('C6.input',await status()=='')
        old=await start(text='removed-output'); await swap('copy-output','#copy-a output'); await finish(old)
        await record('C7.output',await status()=='')
        old=await start(text='independent-note')
        await page.evaluate('''()=>{const n=document.createElement('aside');n.id='copy-note';document.querySelector('#copy-a').append(n)}''')
        await swap('note','#copy-note','delete'); await finish(old)
        await record('C8.retained',await status()=='복사했습니다')
        await page.evaluate('Object.defineProperty(navigator,"clipboard",{value:undefined})')
        await start(text='unsupported'); await record('C9.unsupported',await status()=='복사하지 못했습니다')
        await record('runtime.errors',not errors,errors)
        result={'browser':browser.version,'clipboard':'Controlled Promise stub: no real OS clipboard writes or permission claim','results':results,'requests':requests,'errors':errors}
        (ROOT/'holdout-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)); print(json.dumps(result,ensure_ascii=False,indent=2)); await browser.close()
asyncio.run(run())
