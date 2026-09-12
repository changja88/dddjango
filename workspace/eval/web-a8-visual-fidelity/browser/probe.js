async (page) => {
  const p = await page.context().newPage();
  const out = {browser:await page.context().browser().version(),viewport:{width:390,height:844},states:[]};
  try {
    await p.setViewportSize(out.viewport);
    await p.setContent("<!doctype html>\n<html lang=\"ko\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>이름 등록 — 원본</title><style>* { box-sizing: border-box; }\nhtml, body { margin: 0; }\nbody { min-height: 100vh; display: grid; place-items: center; background: #f6f5f2; color: #292823; font: 14px/1.5 sans-serif; }\n.source-dialog { display: flex; flex-direction: column; width: 344px; height: 316px; padding: 20px; gap: 20px; border-radius: 24px; background: #ffffff; }\nh1 { margin: 0; font-size: 20px; line-height: 28px; }\n.source-scroll { display: flex; flex-direction: column; flex: 1 1 auto; min-height: 0; gap: 24px; overflow-y: auto; padding: 2px 2px 4px; }\n.source-step { display: flex; flex-direction: column; gap: 24px; }\n.source-field { display: flex; flex-direction: column; gap: 8px; }\n.source-label { font-size: 13px; line-height: 20px; color: #646159; }\n.source-input { display: flex; align-items: center; gap: 10px; width: 100%; height: 52px; padding: 0 14px; border: 1px solid #d5d1c7; border-radius: 16px; background: #ffffff; transition: border-color 160ms ease, box-shadow 160ms ease; }\n.source-input:focus-within { border-color: #8f675b; box-shadow: 0 0 0 3px rgba(143, 103, 91, .18); }\n.source-icon { flex: 0 0 auto; font-size: 18px; line-height: 20px; color: #888276; }\n.source-input input { flex: 1 1 auto; min-width: 0; width: 100%; padding: 0; border: 0; outline: none; color: inherit; background: transparent; font: inherit; }\n.source-input input::placeholder { color: #888276; }\n.source-note { margin: 0; color: #646159; font-size: 13px; line-height: 20px; }\nbutton { height: 44px; flex: 0 0 auto; border: 0; border-radius: 14px; background: #8f675b; color: #ffffff; font: inherit; }\n</style></head>\n<body><main class=\"source-dialog\" aria-labelledby=\"form-title\"><h1 id=\"form-title\">관계인 등록</h1><div class=\"source-scroll\"><div class=\"source-step\"><label class=\"source-field\"><span class=\"source-label\">이름</span><span class=\"source-input\"><span class=\"source-icon\" aria-hidden=\"true\">○</span><input id=\"person-name\" placeholder=\"이름을 입력해주세요\" autocomplete=\"off\"></span></label><p class=\"source-note\">상담할 사람의 이름을 적어주세요.</p></div></div><button type=\"button\">다음</button></main></body></html>\n");
    for (const [name,padding] of [['source','2px 2px 4px'],['omitted','0px'],['room-control','4px']]) {
      await p.locator('.source-scroll').evaluate((el,pad)=>el.style.padding=pad,padding);
      await p.locator('#form-title').click();
      await p.waitForTimeout(220);
      await p.screenshot({path:"/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/browser"+'/'+name+'-default.png',style:'input { caret-color:transparent; }'});
      await p.locator('#person-name').focus();
      await p.waitForTimeout(220);
      const geometry=await p.locator('.source-input').evaluate(el=>{
        const r=el.getBoundingClientRect(),s=el.closest('.source-scroll'),sr=s.getBoundingClientRect(),cs=getComputedStyle(s);
        return {input:{x:r.x,y:r.y,width:r.width,height:r.height},parent:{x:sr.x,y:sr.y,width:sr.width,height:sr.height},padding:cs.padding,overflowX:cs.overflowX,overflowY:cs.overflowY,boxShadow:getComputedStyle(el).boxShadow,focused:document.activeElement.id};
      });
      await p.screenshot({path:"/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/browser"+'/'+name+'-focus.png',style:'input { caret-color:transparent; }'});
      out.states.push({name,...geometry,captures:[name+'-default.png',name+'-focus.png']});
    }
    return out;
  } finally { await p.close(); }
}
