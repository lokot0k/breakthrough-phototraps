import {LoaderFunctionArgs, Navigate, useLoaderData} from "react-router-dom";
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

const tagToColor = {
    [QualityTag.ANIMAL]: "#28a745",
    [QualityTag.EMPTY]: "#ffc107",
    [QualityTag.BROKEN]: "#dc3545",
}

const tagToDescription = {
    [QualityTag.ANIMAL]: "Животное",
    [QualityTag.EMPTY]: "Пустое",
    [QualityTag.BROKEN]: "Поврежеденное",
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

export function Result() {
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
    }

    const result = [] as ExtendedReactImageGalleryItem[]
    for (const key in loadedData) {
        result.push(...loadedData[key as QualityTag].map(value => ({
            original: value,
            thumbnail: value,
            originalHeight: 600,
            description: tagToDescription[key as QualityTag],
            originalTag: key as QualityTag,
            thumbnailClass: `thumbnail-${key}`,
            originalClass: `original-${key}`,
        })))
    }
    const images = result.sort((a, b) => a.original.localeCompare(b.original))


    return <div className="App">
        <header className="App-header">
            <p>Тигерекский заповедник</p>
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
                    <a><FontAwesomeIcon icon={solid("download")}/>Скачать CSV</a>
                    <a><FontAwesomeIcon icon={solid("download")}/>Скачать ZIP</a>
                </div>
            </div>
            <div className="image-gallery-container">
                <ImageGallery items={result.filter(filterFunc)} lazyLoad thumbnailPosition="left"/>
            </div>
        </div>
    </div>;
}