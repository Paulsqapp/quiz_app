/* after dom has loaded 
        asign numbers to input type

*/

const text_inputs = document.getElementsByTagName('input')
const select_box = document.getElementsByTagName('select')
const text_box = document.getElementsByTagName('textarea')
const tables = document.getElementsByTagName('table')
const forms = document.getElementsByTagName('form')

console.log('text area', text_box)

for(var i = 1; i < text_inputs.length; i++){
        if (text_inputs[i].type != 'hidden') {
        console.log(text_inputs[i].name)
        text_inputs[i].name = text_inputs[i].name + '_' +  i
        text_inputs[i].value = i
        console.log(text_inputs[i].name)
        }
}

for(var i = 1; i < select_box.length; i++){
        console.log(select_box[i])
    select_box[i].name = select_box[i].name + '_' + i
    select_box[i].className = 'form-control'
}
console.log('text area 001', + text_box.length )
for(var i = 1; i < text_box.length; i++){
        console.log('text area' )
    text_box[i].name = text_box[i].name + '_' + i
    text_box[i].className = 'form-control-plaintext'
}

