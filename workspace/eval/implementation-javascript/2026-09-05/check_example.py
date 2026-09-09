import asyncio, json, sys
from pathlib import Path
from playwright.async_api import async_playwright

async def run(label):
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
        page=await browser.new_page(); results=[]; errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        await page.goto('http://127.0.0.1:8771/example/',wait_until='networkidle')
        async def state():return await page.locator('#password-a').evaluate('(r)=>({type:r.querySelector("input").type,hidden:r.querySelector("button").hidden,pressed:r.querySelector("button").getAttribute("aria-pressed")})')
        async def record(id,ok):results.append({'id':id,'pass':bool(ok)})
        async def swap(kind,target):
            await page.evaluate('([kind,target])=>htmx.ajax("GET","/fragment/"+kind,{target,swap:"outerHTML"})',[kind,target]);await page.wait_for_timeout(80)
        await record('P1.initial',not (await state())['hidden'])
        await page.locator('#password-a button').focus();await page.locator('#password-a button').press('Enter')
        await record('P2.keyboard', (await state())['type']=='text' and (await state())['pressed']=='true')
        await record('P3.isolation',await page.locator('#password-b input').get_attribute('type')=='password')
        await swap('password-root','#password-a'); await record('P4.root',not (await state())['hidden'])
        await swap('password-button','#password-a button');await record('P5.child-button',not (await state())['hidden'])
        await page.locator('#password-a button').evaluate('(b)=>b.click()')
        await swap('password-input','#password-a input');await record('P6.child-input',(await state())['pressed']=='false')
        await record('runtime.errors',not errors)
        result={'label':label,'results':results,'errors':errors};(Path(__file__).parent/f'example-{label}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));await browser.close()
asyncio.run(run(sys.argv[1]))
