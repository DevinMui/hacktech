// works on ebay search page: https://www.ebay.com/sch/i.html

function getResults() {
    return document.querySelectorAll('ul.srp-results.srp-list.clearfix>li')
    // arr.map(doSomething)
}

function waitFor(selector) {
    let time = 2000
    return new Promise(function (res, rej) {
        waitForElementToDisplay(selector, time);
        function waitForElementToDisplay(selector) {
            if (document.querySelector(selector) != null) {
                res(document.querySelector(selector));
            }
            else {
                setTimeout(function () {
                    waitForElementToDisplay(selector, time);
                }, time);
            }
        }
    });
}


console.log('extension active')
waitFor('ul.srp-results.srp-list.clearfix>li').then(afterLoad).catch(console.log)

function afterLoad() {
    let searchResults = getResults()
    searchResults.forEach(i=>addPlus(i))
}

function addPlus(elem) {
    let inside = document.createElement('d')
    inside.innerHTML = ('<div class="add-to-queue-btn">Add to Queue</div>')
    inside.addEventListener('click', console.log)
    elem.appendChild(inside)
}
 
function createModal() {

}

