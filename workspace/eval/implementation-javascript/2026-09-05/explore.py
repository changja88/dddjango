import asyncio, json, sys
from pathlib import Path
from playwright.async_api import async_playwright
from check import PNG

async def run(mode):
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True)
        page = await browser.new_page()
        await page.goto(f'http://127.0.0.1:8771/{mode}/', wait_until='networkidle')
        await page.locator('#preview-a input').set_input_files({'name':'photo.png','mimeType':'image/png','buffer':PNG})
        await page.wait_for_function('document.querySelector("#preview-a img").naturalWidth>0')
        await page.evaluate('''()=>{ const note=document.createElement('aside'); note.id='note'; note.textContent='독립 안내'; document.querySelector('#preview-a').append(note); const b=document.createElement('button'); b.id='delete-note'; b.textContent='안내 닫기'; b.setAttribute('hx-get','/fragment/note'); b.setAttribute('hx-target','#note'); b.setAttribute('hx-swap','delete'); document.body.append(b); htmx.process(b); }''')
        async with page.expect_response(lambda r:'/fragment/note' in r.url): await page.locator('#delete-note').click()
        await page.wait_for_selector('#note',state='detached')
        observed = await page.locator('#preview-a').evaluate('(r)=>({files:r.querySelector("input").files.length,hidden:r.querySelector("img").hidden,src:r.querySelector("img").getAttribute("src"),name:r.querySelector("output").textContent})')
        result={'id':'E1','mode':mode,'pass': observed['files']==1 and not observed['hidden'] and observed['name']=='photo.png' and bool(observed['src']),'observed':observed}
        (Path(__file__).parent/f'{mode}-explore.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
        print(json.dumps(result,ensure_ascii=False)); await browser.close()

if __name__=='__main__': asyncio.run(run(sys.argv[1]))
