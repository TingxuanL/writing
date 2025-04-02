var second = 0;
// var myInterval = setInterval(timer, 1000);

var selectStart = selectEnd = -1;
var inputTextArea = document.getElementById("EnglishWriting");

if (document.getElementById("WritingForm")) {
    document.getElementById("WritingForm").addEventListener('submit', event => {
        record["submitTime"] = new Date().getTime();
        json_string = JSON.stringify(record);
        document.getElementById("examRecord").value = json_string;
        if (auto_save_json) {
            saveTemplateAsFile(json_file_name, json_string);
        }
    });
}

// document.getElementById("EnglishWriting").addEventListener('click', event => {
//     // console.log("click" + document.getElementById("EnglishWriting").selectionStart) // logs previous location
//     // return false;
//     // alert("No selection is allowed!");
//     selectStart = selectEnd = -1;
//     inputTextArea.selectionStart = inputTextArea.selectionEnd;
//     return false;
// });

// document.getElementById("EnglishWriting").addEventListener('mousedown', event => {
//     console.log("mousedown" + document.getElementById("EnglishWriting").selectionStart) // logs previous location
//     // return false;
//     // event.preventDefault();
// });

// document.getElementById("EnglishWriting").addEventListener('mouseup', event => {
//     console.log("mouseup" + document.getElementById("EnglishWriting").selectionStart) // logs previous location
//     return false;
// });

// document.getElementById("EnglishWriting").addEventListener('select', event => {
//     alert("No selection is allowed!");
//     selectionRange = getInputSelection(inputTextArea);
//     selectStart = selectionRange.start;
//     selectEnd = selectionRange.end;
//         // alert("No selection is allowed!");
//         selectStart = selectEnd = -1;
//         inputTextArea.selectionStart = inputTextArea.selectionEnd;
//     // event.preventDefault();
//     // return false;
// });


var record = {"startTime": new Date().getTime(), "sequences": []};

if (localStorage.getItem("second") != null) {
    second = localStorage.getItem("second");
    document.getElementById("TimeMinute").innerText = second;
}

function timer() {
    second++;
    document.getElementById("TimeMinute").innerText = second;
    document.getElementById("EnglishWriting").focus();
}

function getInputSelection(el) {
    var start = 0, end = 0, normalizedValue, range,
        textInputRange, len, endRange;

    if (typeof el.selectionStart == "number" && typeof el.selectionEnd == "number") {
        start = el.selectionStart;
        end = el.selectionEnd;
    } else {
        range = document.selection.createRange();

        if (range && range.parentElement() == el) {
            len = el.value.length;
            normalizedValue = el.value.replace(/\r\n/g, "\n");

            // Create a working TextRange that lives only in the input
            textInputRange = el.createTextRange();
            textInputRange.moveToBookmark(range.getBookmark());

            // Check if the start and end of the selection are at the very end
            // of the input, since moveStart/moveEnd doesn't return what we want
            // in those cases
            endRange = el.createTextRange();
            endRange.collapse(false);

            if (textInputRange.compareEndPoints("StartToEnd", endRange) > -1) {
                start = end = len;
            } else {
                start = -textInputRange.moveStart("character", -len);
                start += normalizedValue.slice(0, start).split("\n").length - 1;

                if (textInputRange.compareEndPoints("EndToEnd", endRange) > -1) {
                    end = len;
                } else {
                    end = -textInputRange.moveEnd("character", -len);
                    end += normalizedValue.slice(0, end).split("\n").length - 1;
                }
            }
        }
    }

    return {
        start: start,
        end: end
    };
}

function keyboardInput(event) {
    timeNow = new Date();
    positionInfo = getInputSelection(inputTextArea);
    // currentText = document.getElementById("examRecord").value;
    // document.getElementById("examRecord").value = currentText + '|' + positionInfo.start + ',' + event.data + ',' + event.inputType + ',' + timeNow.getTime();
    // console.log(positionInfo);
    
        record["sequences"].push({"selectStart": selectStart,
                                  "selectEnd": selectEnd,
                                  "position": positionInfo.start-1,
                                  "data": event.data,
                                  "inputType": event.inputType,
                                  "time": timeNow.getTime(),
                                  "article": inputTextArea.value,
                                });
    selectStart = -1;
    selectEnd = -1;
    
    // document.getElementById("examRecord").value = JSON.stringify(record);
}

async function replayRecord() {
    // clearInterval(myInterval);
    // myInterval = setInterval(timer, 1000);
    inputTextArea.value = "";
    sequences = record["sequences"];
    org_startTime = startTime = record["startTime"];
    for (i=0; i < sequences.length; ++i) {
        r = sequences[i];
        // console.log(r);
        position = r["position"];
        data = r["data"];
        inputType = r["inputType"];
        t_selectStart = r["selectStart"]
        t_selectEnd = r["selectEnd"]
        waitTime = r["time"] - startTime;
        startTime = r["time"];
        if (i > 0) {
            await sleep(waitTime/10);
        }
        second = Math.floor((startTime - org_startTime)/1000/60)
        document.getElementById("TimeMinute").innerText = second;
        if (r.hasOwnProperty("article")) {
            inputTextArea.value = r["article"];
        } else {
            switch (inputType) {
                case "insertText":
                    currentValue = inputTextArea.value;
                    if (t_selectStart == t_selectEnd) {
                        if (data == null) {
                            data = "\n";
                        }
                        inputTextArea.value = currentValue.slice(0, position) + data + currentValue.slice(position, currentValue.length);
                    } else {
                        inputTextArea.value = currentValue.slice(0, t_selectStart) + data + currentValue.slice(t_selectEnd, currentValue.length);
                    }
                    break;
                case "deleteContentBackward":
                case "deleteContentForward":
                    currentValue = inputTextArea.value;
                    if (t_selectStart == t_selectEnd) {
                        inputTextArea.value = currentValue.slice(0, position+1) + currentValue.slice(position+2, currentValue.length);
                    } else {
                        inputTextArea.value = currentValue.slice(0, t_selectStart) + currentValue.slice(t_selectEnd, currentValue.length);
                    }
                    break;
                case "insertLineBreak":
                    currentValue = inputTextArea.value;
                    data = "\n";
                    if (t_selectStart == t_selectEnd) {
                        inputTextArea.value = currentValue.slice(0, position) + data + currentValue.slice(position, currentValue.length);
                    } else {
                        inputTextArea.value = currentValue.slice(0, t_selectStart) + data + currentValue.slice(t_selectEnd, currentValue.length);
                    }
                    break;
                case "insertReplacementText":
                    console.warn("It uses insertReplacementText probably by grammarly or system auto correction!")
                    // currentValue = inputTextArea.value;
                    // if (t_selectStart == t_selectEnd) {
                    //     inputTextArea.value = currentValue.slice(0, position) + data + currentValue.slice(position, currentValue.length);
                    // } else {
                    //     inputTextArea.value = currentValue.slice(0, t_selectStart) + data + currentValue.slice(t_selectEnd, currentValue.length);
                    // }
                    break;
                default:
                    console.warn("Unhandled events")
                    console.warn(r);
            }
        }
    }
    // clearInterval(myInterval);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


// document.onkeydown = function(e) {
//     if (((e.ctrlKey || e.metaKey) && e.key === 'z') || ((e.ctrlKey || e.metaKey) && e.key === 'y'))  {
//       e.preventDefault();
//       alert("No redo or undo!");
//     }
//   }


const saveTemplateAsFile = (filename, json_string) => {
    const blob = new Blob([json_string], { type: "text/json" });
    const link = document.createElement("a");

    link.download = filename;
    link.href = window.URL.createObjectURL(blob);
    link.dataset.downloadurl = ["text/json", link.download, link.href].join(":");

    const evt = new MouseEvent("click", {
        view: window,
        bubbles: true,
        cancelable: true,
    });

    link.dispatchEvent(evt);
    link.remove()
};