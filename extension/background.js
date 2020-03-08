function checkToken() {
  if(!chrome.storage.sync.get('auth')) return false
  return true
}

chrome.browserAction.onClicked.addListener(function(tab) {
  if(checkToken())
    return chrome.tabs.create({'url': chrome.extension.getURL('popup.html'), 'selected': true});
  chrome.tabs.create({'url': chrome.extension.getURL('login_page.html'), 'selected': true});
});