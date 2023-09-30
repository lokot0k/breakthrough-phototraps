import React, {DragEventHandler, useRef, useState} from 'react';
import './App.css';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {solid} from "@fortawesome/fontawesome-svg-core/import.macro";
import {Result} from "./Result";
import {redirect, useNavigate} from "react-router-dom";

interface Response {
    success: boolean
    empty: string[]
    broken: string[]
    animal: string[]
}

function Welcome() {
    const [url, setUrl] = useState("");
    const [isLoading, setLoading] = useState(false)
    const [dragActive, setDragActive] = useState(false)
    const inputRef: React.MutableRefObject<null | HTMLInputElement> = useRef(null);
    const nav = useNavigate();

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

    const handleFile = async (file: File) => {
        if (file.type !== "application/zip") {
            alert("File must be a zip archive")
            return
        }
        const formData = new FormData();
        formData.append("docfile", file);
        try {
            setLoading(true)
            const response = await fetch("/api/do_good/", {
                method: "POST",
                body: formData,
            });
            if (response.ok) {
                const body = await response.json() as Response
                nav("/result");
            } else {
                alert("Произошла ошибка")
                setLoading(false)
            }
        } catch (e) {
            alert("Произошла ошибка")
            console.log(e)
            setLoading(false)
        }
    }
    // console.log(file)


    const onButtonClick = () => {
        inputRef.current?.click();
    };


    const onUrlSend = async () => {
        // regex for google drive url
        const regex = /https:\/\/drive\.google\.com\/drive\/folders\/([a-zA-Z0-9_-]+)\/?(view)?(\?usp=sharing)?/;
        if (!url.match(regex)) {
            alert("Неверная ссылка");
            return;
        }
        try {
            const id = url.match(regex)![1];
            console.log(id);
            const body = {
                folder: id
            }
            setLoading(true)
            const response = await fetch("/api/do_good_url/", {
                method: "POST",
                body: JSON.stringify(body),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                nav("/result");
            } else {
                alert("Произошла ошибка")
                setLoading(false)
            }
        } catch (e) {
            alert("Произошла ошибка")
            console.log(e)
            setLoading(false)
        }
    };

    return <div className="Welcome">
        <header className="Welcome-header">
            <form onDragOver={handleDrag} onDragEnter={handleDrag} onDragLeave={handleDrag} onDrop={handleDrop}
                  onSubmit={(e) => e.preventDefault()}>
                <input ref={inputRef} id="file-upload" type="file" onChange={handleChange}/>
                <label id="label-file-upload" htmlFor="file-upload" className={dragActive ? "drag-active" : ""}>
                    <div>
                        <button onClick={onButtonClick} className="upload-button"><FontAwesomeIcon
                            icon={solid("upload")} bounce/>Загрузить архив
                        </button>
                    </div>
                </label>
                <span className="or">или</span>
                <br/>
                <div className="file-url">
                    <input className="file-url-input" placeholder="Ссылка на гугл диск..." value={url}
                           onChange={event => setUrl(event.target.value)}/>
                    <span className="file-url-button" onClick={onUrlSend}><FontAwesomeIcon
                        icon={solid("arrow-right")}/></span>
                </div>
            </form>
        </header>
        {isLoading ? (<div className="progress-bar-container">
            <div className="progress-bar">
                <div className="circle circle-border"/>
            </div>
        </div>) : <></>}
    </div>
}

export default Welcome;
