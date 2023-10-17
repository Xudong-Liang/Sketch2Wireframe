/*
 * Sample plugin scaffolding for Adobe XD.
 *
 * Visit http://adobexdplatform.com/ for API docs and more sample code.
 */
 const fs = require("uxp").storage.localFileSystem;
 const {Rectangle, Color,ImageFill,Artboard,Text,Line} = require("scenegraph");
 const formats = require("uxp").storage.formats;
 let application = require("application");
 let img =new ArrayBuffer();
 var data;
//  let dialog;
 async function upload(selection) {
    // Get the dialog element
    const dialog = getDialog();
    // Show the dialog and get a result when the user closes it
    const result = await dialog.showModal();
  
    if (result === "cancel") {
      // Exit if the user cancels the modal
      dialog.close();
    console.log("--------------------cancle");
    return;
      
    }else{
      
      if (img.byteLength==0){
        console.log("no");
        console.log(typeof(img));
        return ;
      }else{
        console.log("--------------------srever");
        const photoUrl = "http://127.0.0.1:5000/sketch";
        data = await xhrBinary(photoUrl);
        console.log(data)
        return console.log(`Your name is ${result}.\n`);
      }
    }
  }


 

 async function uploadSketch(){
  console.log("--------------------upload");
  // dialog.close("reasonCanceled");
  // dialog.remove();
  const file = await fs.getFileForOpening({ types: ["png","jpg"] });

  if (!file) {
      // no files selected
      console.log("upload--");
      return;
  }

  // console.log(file.length);
  img = await file.read({format: formats.binary}); // 'data' is an ArrayBuffer
  console.log("File is " + img.byteLength + " bytes long.");
  
  return;
 }

 function xhrBinary(url) {
  return new Promise((resolve, reject) => {
      const req = new XMLHttpRequest();
      req.onload = () => {
          if (req.status === 200) {
              try {
                  
                  const arr = req.response;
                  console.log(arr);
                  resolve(arr);
              } catch (err) {
                  reject('Couldnt parse response. ${err.message}, ${req.response}');
              }
          } else {
              reject('Request had an error: ${req.status}');
          }
      }
      req.onerror = reject;
      req.onabort = reject;
      req.open('POST', url, true);
      req.responseType = "json";
      
      console.log(img.byteLength);
      req.send(img);
  })};
 function getDialog() {
    // Get the dialog if it already exists
    let dialog = document.querySelector("dialog");
  
    if (dialog) {
      // dialog.showModal();
      console.log("Dialog already loaded in DOM. Reusing...\n");
      return dialog;
    } else {
      // Otherwise, create and return a new dialog
      return createDialog();
    }
  }
  
  function createDialog() {
    console.log(
      "Adding dialog to DOM.\nIt will remain in the DOM until you call `dialog.remove()`, or your plugin is reloaded by XD.\n"
    );
  
    //// Add your HTML to the DOM
    document.body.innerHTML = `
      <style>
          dialog {
              width: 400px;
          }
          h1 {
              display: flex;
              align-items: center;
              justify-content: space-between;
          }
          .icon {
              width: 24px;
              height: 24px;
              overflow: hidden;
          }
          .ai-upload-zone {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 1px dashed #ccc;
            background: #f7f7f7;
            cursor: pointer;
         }
         .ai-upload-zone-icon.ai-icon {
            font-size: 64px;
            margin-bottom: 8px;
            color: #1a73e8;
         }
      </style>
      <dialog>
          <form method="dialog">
              <h1><span>Sketch Transform</span><img class="icon" src="images/icon@1x.png"></h1>
              <hr />
              <h2><span>Add sketch</span></h2>
              
              <div id="upload" class="ai-upload-zone" data-hover="false" data-disabled="false" style="width: 100%; height: 280px;">
                <i class="ai-icon ai-upload-zone-icon" style="color: #1a73e8">
                  <svg width="1em" height="1em" viewBox="0 0 32 32" fill="currentColor"><path d="M5.5 17v8h21v-8h2v10h-25V17h2zM15.941 4.586l5.762 5.703-1.406 1.422L17 8.448V19h-2V8.379l-3.29 3.324-1.42-1.406 5.651-5.711z"></path></svg>
                </i>
                <div class="ai-upload-zone-main-tip">upload pictures form computer</div>
              </div>
              <footer>
                <button id="cancel">Cancel</button>
                <button type="submit" id="ok" uxp-variant="cta">OK</button>
              </footer>
          </form>
      </dialog>
    `;

    const [dialog,upload,ok, cancel] = [
        "dialog",
        "#upload",
        "#ok",
        "#cancel"
      ].map(s => document.querySelector(s));
    
      //// Add event handlers
      // Close dialog when cancel is clicked, with an optional return value.
      // Note that XD handles the ESC key for you, also returning "reasonCanceled"
      ok.addEventListener("click", e => handleSubmit(e, dialog));
      cancel.addEventListener("click", () => dialog.close("cancel"));
      // Handle ok button click
      
      upload.addEventListener("click",() => uploadSketch());
      // Handle form submit via return key
      // form.onsubmit = e => handleSubmit(e, dialog);
     
      return dialog;
    }
// const {Rectangle, Color} = require("scenegraph"); 


function randomString(e) {  
  e = e || 32;
  var t = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678",
  a = t.length,
  n = "";
  for (var i = 0; i < e; i++) n += t.charAt(Math.floor(Math.random() * a));
  return n
}

async function sketchTransform(selection){
  
  let root = data[0]
  // console.log(root)
  let node = selection.items[0];
  // 调整画布大小和位置
  node.resize(Math.ceil(root["bbox"][2] + 60),Math.ceil(root["bbox"][3] + 60))
  const pluginFolder = await fs.getPluginFolder();
  const img =await pluginFolder.getEntry("images/component/Image.png")
  console.log("drawn")
  let x0 = Math.ceil(root["bbox"][0])-30
  let y0 = Math.ceil(root["bbox"][1])-30
  console.log("---------")
  console.log(data)
  while(data.length>0){
    let cur = data.shift()
    
    console.log(typeof(data))

    console.log(typeof(cur.child))


    if(cur.child.length>0){
      var i;
      for(i in cur["child"]){
        data.push(cur["child"][i])
      }
    }
    console.log(data)
    console.log("---------")
      var copClass = cur['category']
      var x = Math.ceil(cur.bbox[0])
      var y = Math.ceil(cur.bbox[1])
      var w = Math.ceil(cur.bbox[2])
      var h = Math.ceil(cur.bbox[3])
      const pluginFolder = await fs.getPluginFolder();
      if(copClass=='image'){
        const img =await pluginFolder.getEntry("images/component/Image.png")
        const imageFill = new ImageFill(img);
        const newElement = new Rectangle();
        newElement.width = w;
        newElement.height = h;
        newElement.fill = imageFill;
        newElement.stroke = new Color("gray");
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0);
      }else if(copClass=='button'){
        const img =await pluginFolder.getEntry("images/component/Button.png")
        const imageFill = new ImageFill(img);
        const newElement = new Rectangle();
        newElement.height = h;
        newElement.width = w;
        newElement.fill = imageFill;
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0);
      }else if(copClass=='checkbox'){
        const img =await pluginFolder.getEntry("images/component/Checkbox.png")
        const imageFill = new ImageFill(img);
        const newElement = new Rectangle();
        newElement.width = w;
        newElement.height = imageFill.naturalHeight*w/imageFill.naturalWidth;
        newElement.fill = imageFill;
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0);
      }else if(copClass=='radiobutton'){
        const img =await pluginFolder.getEntry("images/component/Radio.png")
        const imageFill = new ImageFill(img);
        const newElement = new Rectangle();
        newElement.width = w;
        newElement.height = imageFill.naturalHeight*w/imageFill.naturalWidth;
        newElement.fill = imageFill;
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0);
      }else if(copClass=='slider'){
        const img =await pluginFolder.getEntry("images/component/Slider.png")
        const imageFill = new ImageFill(img);
        const newElement = new Rectangle();
        newElement.width = w;
        newElement.height = imageFill.naturalHeight*w/imageFill.naturalWidth;
        newElement.fill = imageFill;
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0);
      }else if(copClass=='toggle'){
        const img =await pluginFolder.getEntry("images/component/Toggle.png")
        const imageFill = new ImageFill(img);
        const newElement = new Rectangle();
        newElement.width = w;
        newElement.height = imageFill.naturalHeight*w/imageFill.naturalWidth;
        newElement.fill = imageFill;
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0);
      }else if(copClass=='dropdown'){
        const img =await pluginFolder.getEntry("images/component/Dropdown.png")
        const imageFill = new ImageFill(img);
        const newElement = new Rectangle();
        newElement.height = h;
        newElement.width = imageFill.naturalWidth*h/imageFill.naturalHeight;
        newElement.fill = imageFill;
        newElement.stroke = new Color("gray");
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0);
      }else if(copClass=='video'){
        const img =await pluginFolder.getEntry("images/component/Video.png")
        const imageFill = new ImageFill(img);
        const newElement = new Rectangle();
        newElement.width = w;
        newElement.height = h;
        newElement.fill = imageFill;
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0);
      }else if(copClass=='textinput' || copClass=='textarea'){
        const img =await pluginFolder.getEntry("images/component/Input.png")
        const imageFill = new ImageFill(img);
        const newElement = new Rectangle();
        newElement.width = w;
        newElement.height = h;
        newElement.fill = imageFill;
        newElement.stroke = new Color("gray");
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0);
      }else if(copClass=='linebreak'){
        const line = new Line();
        line.setStartEnd(                           
          x-x0,
          Math.ceil(y-y0+h/2),
          x-x0+w,
          Math.ceil(y-y0+h/2)
        );
        line.strokeEnabled = true;
        line.stroke = new Color("gray");
        line.strokeWidth = 3;
        // line.push(line);
        selection.insertionParent.addChild(line); 
      }else if(copClass=='container'){
        const newElement = new Rectangle();
        newElement.width = w;
        newElement.height = h;
        newElement.stroke = new Color("gray");
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0); 
      }else if(copClass=='link'){
        const newElement = new Text();
        newElement.layoutBox = {type:Text.FIXED_HEIGHT,width:w,height:h}
        newElement.text = "link";
        newElement.styleRanges = [{
            fill: new Color("blue"),
            fontSize: h,
            underline: true
        }];
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0+9);
      }else if(copClass=='header'){
        const newElement = new Text();
        newElement.layoutBox = {type:Text.FIXED_HEIGHT,width:w,height:h}
        newElement.text = "TITLE";
        newElement.styleRanges = [{
            fill: new Color("black"),
            fontSize: h,
        }];
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0+9);
      }else if(copClass=='label'){
        const newElement = new Text();
        newElement.text = "label";

        newElement.styleRanges = [{
            length: w,
            fill: new Color("black"),
            fontSize: h,
        }];
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0);
      }else if(copClass=='paragraph'){
        const newElement = new Text();
        newElement.layoutBox = {type:Text.FIXED_HEIGHT,width:w,height:h}
        var n = Math.ceil(cur.area/30)
        newElement.text = randomString(n);

        newElement.styleRanges = [{
            
            fill: new Color("gray"),
            fontSize: 30,
        }];
        selection.insertionParent.addChild(newElement);
        newElement.moveInParentCoordinates(x-x0,y-y0+9);
      }
      
    }

  }


// async function drownComponent(selection,node){
//   var copClass = node['category']
//   var x = Math.ceil(root["bbox"][0])
//   var y = Math.ceil(root["bbox"][1])
//   var w = Math.ceil(root["bbox"][2])
//   var h = Math.ceil(root["bbox"][3])
//   if(copClass=='image'){
//     const pluginFolder = await fs.getPluginFolder();
//     const img =await pluginFolder.getEntry("images/component/Image.png")
//     const imageFill = new ImageFill(img);
//     const newElement = new Rectangle();
//     newElement.width = w;
//     newElement.height = h;
//     newElement.fill = imageFill;
//     selection.insertionParent.addChild(newElement);
//     newElement.moveInParentCoordinates(100, 100);
//   }else if(copClass=='image')
// }



function rectangleHandlerFunction(selection) { 

    const newElement = new Rectangle(); 
    newElement.width = 100;
    newElement.height = 50;
    newElement.fill = new Color("Purple");

    selection.insertionParent.addChild(newElement);
    newElement.moveInParentCoordinates(100, 100);

}

module.exports = {
    commands: {
        showcomponents: rectangleHandlerFunction,
        upload,
        sketchTransform
    }
    
};
