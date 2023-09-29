import React, {DragEventHandler, useRef, useState} from 'react';
import './App.css';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {solid} from "@fortawesome/fontawesome-svg-core/import.macro";

function Welcome() {
    const [dragActive, setDragActive] = useState(false)
    const inputRef: React.MutableRefObject<null | HTMLInputElement> = useRef(null);

    const handleDrag: DragEventHandler = (e) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === "dragover" || e.type === "dragenter") {
            setDragActive(true)
        } else if (e.type === "dragleave") {
            setDragActive(false)
        }
    }

    const handleDrop: DragEventHandler = (e) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)
        console.log(e.dataTransfer.files)
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0])
        }
    }

    const handleChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
        e.preventDefault()
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0])
        }
    }

    const handleFile = (file: File) => {
        if (file.type !== "application/zip") {
            alert("File must be a zip archive")
            return
        }
        console.log(file)
    }

    const onButtonClick = () => {
        inputRef.current?.click();
    };

    return (
        <div className="App">
            <header className="App-header">
                <form  onDragOver={handleDrag} onDragEnter={handleDrag} onDragLeave={handleDrag} onDrop={handleDrop} onSubmit={(e) => e.preventDefault()}>
                    <input ref={inputRef} id="file-upload" type="file" onChange={handleChange}/>
                    <label id="label-file-upload" htmlFor="file-upload" className={dragActive ? "drag-active" : "" }>
                        <div>
                            <p>Drag and drop image archive (.zip) here or</p>
                            <button onClick={onButtonClick} className="upload-button"><FontAwesomeIcon icon={solid("upload")} bounce/>Upload archive</button>
                        </div>
                    </label>
                    {/*{ dragActive && <div className="drag-overlay" onDragOver={handleDrag} onDragEnter={handleDrag} onDragLeave={handleDrag} onDrop={handleDrop}/> }*/}
                </form>
            </header>
        </div>
    );
}

export default Welcome;
