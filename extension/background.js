function checkToken(succ, fail) {
  chrome.storage.sync.get('auth', e => {
    console.log(e)
    if(e) return succ()
    fail()
  })
}

chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if(request.message === 'security fail') securityFail()
    sendResponse('test')
  });

function securityFail() {
  // invalidate token
  chrome.storage.sync.set({auth: undefined})
}

chrome.browserAction.onClicked.addListener(function(tab) {
  let ct = checkToken(()=>chrome.tabs.create({'url': chrome.extension.getURL('popup.html'), 'selected': true}), ()=>chrome.tabs.create({'url': chrome.extension.getURL('login_page.html'), 'selected': true}))
});