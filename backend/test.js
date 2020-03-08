var url = 'https://hacktech-ebay.appspot.com'
// url = 'https://dfbb8236.ngrok.io'
fetch(url + '/login', {
    method: 'POST',
    mode: 'cors',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'em@em.com' })
})
    .then(res => {
        console.log(res.status)
        return res.json()
    })
    .then(res => console.log(res))
    .catch(err => console.log(err))

fetch('https://dfbb8236.ngrok.io/', {
    method: 'GET',
    mode: 'cors',
    headers: { 'Content-Type': 'application/json' }
})
    .then(res => {
        console.log(res.status)
        return res.json()
    })
    .then(res => console.log(res))
    .catch(err => console.log(err))
