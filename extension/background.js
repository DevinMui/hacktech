function checkToken() {
  if(!chrome.storage.sync.get('auth')) return false
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
  queryInfo = {active: true};
  chrome.tabs.query(queryInfo, function(result) {
    console.log(result)
      var activeTab = result[0].id;
      updateProperties = {'url': chrome.extension.getURL('login_page.html'), 'selected': true};
      chrome.tabs.update(activeTab, updateProperties, function() {
          // Anything else you want to do after the tab has been updated.
      });
  });
}

chrome.browserAction.onClicked.addListener(function(tab) {
  if(checkToken())
    return chrome.tabs.create({'url': chrome.extension.getURL('popup.html'), 'selected': true});
  chrome.tabs.create({'url': chrome.extension.getURL('login_page.html'), 'selected': true});
});