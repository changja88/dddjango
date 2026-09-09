import asyncio, base64, json, sys
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aNu0AAAAASUVORK5CYII=')

async def run(mode):
    results, errors, requests = [], [], []
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True)
        page = await browser.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('response', lambda r: requests.append({'url': r.url, 'status': r.status}) if '/fragment/' in r.url else None)
        await page.goto(f'http://127.0.0.1:8771/{mode}/', wait_until='networkidle')
        async def check(id, ok, detail=''):
            results.append({'id': id, 'pass': bool(ok), 'detail': detail})
        async def select(root, name='photo.png', image=True):
            await page.locator(f'#preview-{root} [data-preview-input]').set_input_files({'name': name, 'mimeType': 'image/png' if image else 'text/plain', 'buffer': PNG if image else b'hello'})
            if image:
                await page.wait_for_function('(id) => {const i=document.querySelector(id+" [data-preview-image]"); return !i.hidden && i.complete && i.naturalWidth>0;}', arg=f'#preview-{root}')
        async def state(root):
            return await page.locator(f'#preview-{root}').evaluate('(r)=>({hidden:r.querySelector("img").hidden, name:r.querySelector("output").textContent, files:r.querySelector("input").files.length, src:r.querySelector("img").getAttribute("src")})')
        async def active(): return await page.evaluate('probe.active.size')
        async def swap(button):
            async with page.expect_response(lambda r: '/fragment/' in r.url and r.status == 200):
                await page.locator(button).click()
            await page.wait_for_timeout(80)
        await select('a'); first = await state('a')
        await page.locator('#preview-a button').click(); cleared = await state('a')
        await check('B1', first['name']=='photo.png' and cleared['hidden'] and cleared['files']==0 and not cleared['src'])
        await select('a','a.png'); await select('b','b.png')
        await check('B2', (await state('a'))['name']=='a.png' and (await state('b'))['name']=='b.png')
        await page.evaluate('''()=>{for(let i=0;i<3;i++) document.querySelector('#preview-a').dispatchEvent(new CustomEvent('htmx:load',{bubbles:true,detail:{elt:document.querySelector('#preview-a')}}));}''')
        before = await page.evaluate('probe.created.length'); await select('a','repeat.png')
        await check('B3', await page.evaluate('probe.created.length')-before <= 1)
        await select('a','<img src=x onerror=alert(1)>.png')
        await check('B8', (await state('a'))['name']=='<img src=x onerror=alert(1)>.png' and await page.locator('#preview-a output *').count()==0)
        await page.locator('#preview-a button').click(); await select('a'); await select('a','bad.txt',False)
        await check('B7', (await state('a'))['hidden'] and await active()<=1 and bool((await state('a'))['name']))
        await select('a'); await swap('#replace-root')
        await check('B6.outer', await active()<=1)
        await select('a','new.png'); await check('B5', (await state('a'))['name']=='new.png')
        await swap('#replace-parent'); await check('B6.parent', await active()==0)
        await select('c','c.png'); await select('a'); await check('B4', (await state('c'))['name']=='c.png')
        await swap('#delete-root'); await check('B6.delete', await page.locator('#preview-a').count()==0 and await active()<=1)
        await check('B9', len(requests)==3 and all(r['status']==200 for r in requests))
        await check('runtime.errors', not errors, errors)
        result={'mode':mode,'browser':browser.version,'htmx':await page.evaluate('htmx.version'),'results':results,'requests':requests,'errors':errors}
        (ROOT / f'{mode}-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
        await browser.close()
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == '__main__': asyncio.run(run(sys.argv[1]))
