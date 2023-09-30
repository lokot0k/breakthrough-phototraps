import {LoaderFunctionArgs, Navigate, useLoaderData, useNavigate} from "react-router-dom";
import ImageGallery, {ReactImageGalleryItem} from "react-image-gallery";
import {ChangeEventHandler, useEffect, useState} from "react";
import {Button, Form} from "react-bootstrap";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {solid} from "@fortawesome/fontawesome-svg-core/import.macro";


enum QualityTag {
    ANIMAL = "animal",
    BROKEN = "broken",
    EMPTY = "empty"
}

type ExtendedReactImageGalleryItem = ReactImageGalleryItem & { originalTag: QualityTag }

type Data = {
    [key in QualityTag]: string[]
}


export const loader = async (): Promise<Data | null> => {
    // ====== api request ========

    const response = await fetch("/api/do_good/", {
        method: "GET",
    })
    let x = await response.json();
    console.log(x)
    return response.ok ? x as Data : null;


}


const tagToDescription = {
    [QualityTag.ANIMAL]: "Животное",
    [QualityTag.EMPTY]: "Пусто",
    [QualityTag.BROKEN]: "С дефектом",
}

const filterToZipUrl: { [key: number]: string } = {
    0: "", // all false
    1: "/media/a.zip", // animal
    2: "/media/e.zip", // empty
    3: "/media/ae.zip", // animal empty
    4: "/media/b.zip", // broken
    5: "/media/ab.zip", // animal broken
    6: "/media/be.zip", // empty broken
    7: "/media/abe.zip", // all true
}

const getUrl = (filter: { [key in QualityTag]: boolean }) => {
    let result = 0;
    for (const key in filter) {
        if (filter[key as QualityTag]) {
            result += 1 << (key === QualityTag.ANIMAL ? 0 : key === QualityTag.EMPTY ? 1 : 2)
        }
    }
    return filterToZipUrl[result]
}


function MyInput({filter, filterState, onChangeFunc}: {
    filter: QualityTag,
    filterState: { [key in QualityTag]: boolean },
    onChangeFunc: ChangeEventHandler<HTMLInputElement>
}) {
    return <>
        <input type="checkbox" id={`cb-${filter}`} checked={filterState[filter]}
               onChange={onChangeFunc}/>
        <label htmlFor={`cb-${filter}`}>{tagToDescription[filter]}</label>
    </>;
}

function downloadFile(url: string, filename: string) {
    const link = document.createElement('a');
    link.href = `http://localhost:8000${url}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

export function Result() {
    const nav = useNavigate();
    const [chosenImage, setChosenImage] = useState(null as null | number);
    const [showGallery, setShowGallery] = useState(false);
    const [filterFunc, setFilterFunc] = useState(() => (_: ExtendedReactImageGalleryItem) => true)
    const [filter, setFilter] = useState({
        [QualityTag.ANIMAL]: true,
        [QualityTag.EMPTY]: true,
        [QualityTag.BROKEN]: true,
    })

    const loadedData = useLoaderData() as Data | null

    if (!loadedData) return <Navigate to="/" replace/>


    const changeFilterCheckbox: ChangeEventHandler<HTMLInputElement> = (e) => {
        const value = e.target.id.slice(3) as QualityTag;
        const newFilter = {
            ...filter,
            [value]: e.target.checked,
        };
        setFilterFunc(() => (item: ExtendedReactImageGalleryItem) => {
            return newFilter[item.originalTag as QualityTag]
        })
        setFilter(newFilter)
        setChosenImage(null)
    }

    const result = [] as ExtendedReactImageGalleryItem[]
    for (const key in loadedData) {
        result.push(...loadedData[key as QualityTag].map(value => ({
            original: value,
            thumbnail: value,
            originalHeight: 750,
            description: tagToDescription[key as QualityTag],
            originalTag: key as QualityTag,
            thumbnailClass: `thumbnail-${key}`,
            originalClass: `original-${key}`,
        })))
    }
    const images = result.sort((a, b) => a.original.localeCompare(b.original))


    return <div className="App">
        <header className="App-header">
            <span className="leave-btn"  onClick={() => nav("/")}><FontAwesomeIcon className="leave-icon" icon={solid("arrow-right-from-bracket")}/> Выход</span>
            {/**/}
            <p>Тигирекский заповедник</p>
        </header>
        <div className="Result">
            <div className="result-header">
                <div className="filter-container">
                    <p>Фильтры</p>
                    <MyInput filter={QualityTag.ANIMAL} filterState={filter} onChangeFunc={changeFilterCheckbox}/>
                    <MyInput filter={QualityTag.EMPTY} filterState={filter} onChangeFunc={changeFilterCheckbox}/>
                    <MyInput filter={QualityTag.BROKEN} filterState={filter} onChangeFunc={changeFilterCheckbox}/>
                </div>
                <div className="buttons-container">
                    <a href="#" onClick={() => downloadFile("/media/submission.csv", "submission.csv")}><FontAwesomeIcon
                        icon={solid("download")}/>Скачать CSV</a>
                    <a href="#" onClick={() => downloadFile(getUrl(filter), "Today.zip")}><FontAwesomeIcon
                        icon={solid("download")}/>Скачать архив</a>
                </div>
            </div>
            {chosenImage !== null ? <div className="image-gallery-container">
                    <button className="close-btn" onClick={_ => setChosenImage(null)}><FontAwesomeIcon
                        icon={solid("close")}/></button>
                    <ImageGallery items={result.filter(filterFunc)} lazyLoad thumbnailPosition="left"
                                  startIndex={chosenImage} />
                </div> :
                <div className="image-grid">
                    {images.filter(filterFunc).map((item, index) => <div key={index} className="image-grid-item">
                            <img src={item.thumbnail} alt={item.description} className={`thumbnail-${item.originalTag}`}
                                 onClick={event => setChosenImage(index)}/>
                        </div>
                    )}
                </div>
            }
        </div>
    </div>;
}