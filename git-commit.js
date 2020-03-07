const name = 'aaronh'
const VideoCapture = require('camera-capture').VideoCapture
const writeFileSync = require('fs').writeFileSync
const fs = require('fs')
const { execSync } = require('child_process')
var FormData = require('form-data');
const fetch = require('node-fetch')

const c = new VideoCapture({
	mime: 'image/png'
})
async function test() {
	await c.initialize()
	let f = await c.readFrame()               // PNG as configured
	f = await c.readFrame('image/jpeg') // jpeg
	const message = process.argv.slice(2).join(' ')
	writeFileSync('tmp.jpg', f.data)

	const formData = new FormData();
	formData.append('img', fs.createReadStream('tmp.jpg'));
	formData.append('name', name);
	formData.append('timestamp', Date.now())
	formData.append('message', message)
	let r = await fetch('https://hacktech-2020.azurewebsites.net/test', {
		method: 'POST',
		body: formData
	})
	execSync(`git commit -m "${message}"`)
}
test().then(process.exit).catch(()=>{console.log('fail'); process.exit()})
