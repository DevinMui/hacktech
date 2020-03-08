function checkToken() {
  if(!chrome.storage.sync.get('auth', ()=>{})) return false
  return true
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
  if(checkToken())
    return chrome.tabs.create({'url': chrome.extension.getURL('popup.html'), 'selected': true});
  chrome.tabs.create({'url': chrome.extension.getURL('login_page.html'), 'selected': true});
});