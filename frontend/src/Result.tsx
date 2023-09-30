import {LoaderFunctionArgs, Navigate, useLoaderData} from "react-router-dom";
import ImageGallery, {ReactImageGalleryItem} from "react-image-gallery";
import {ChangeEventHandler, useState} from "react";
import {Form} from "react-bootstrap";

enum QualityTag {
    NONE = "none",
    ANIMAL = "animal",
    BROKEN = "broken",
    EMPTY = "empty"
}

interface ImageData {
    url: string
    qualityTag: QualityTag
}

interface LoadedData {
    images: ImageData[]
    archives: Record<QualityTag, string>
}

export const loader = async ({request}: LoaderFunctionArgs): Promise<LoadedData | null> => {
    const query = new URLSearchParams(request.url.split("?").slice(-1)[0])

    const uuid = query.get("uuid");
    if (!uuid) return null;
    const page = +(query.get("page") || 1)

    // ====== api request ========

    return {
        images: [
            {url: "/image1.jpg", qualityTag: QualityTag.ANIMAL},
            {url: "/image2.jpg", qualityTag: QualityTag.BROKEN},
            {url: "/image3.jpg", qualityTag: QualityTag.EMPTY},
        ].concat(Array(200).fill({url: "/image1.jpg", qualityTag: "animal"})) as ImageData[],
        archives: {
            "animal": "archive_good.zip",
            "broken": "archive_so-so.zip",
            "empty": "archive_bad.zip",
            "none": ""
        },
    }
}


function MyInput({filter, filterState, onChangeFunc}: {
    filter: QualityTag,
    filterState: QualityTag,
    onChangeFunc: ChangeEventHandler<HTMLInputElement>
}) {
    return <>
        <input type="radio" value={filter} id={`radio-${filter}`} checked={filterState === filter}
               onChange={onChangeFunc}/>
        <label htmlFor={`radio-${filter}`}>{filter[0].toUpperCase() + filter.slice(1)}</label>
    </>;
}

export function Result() {
    const [filterFunc, setFilterFunc] = useState(() => (_: ImageData) => true)
    const [filter, setFilter] = useState(QualityTag.NONE)
    const loadedData = useLoaderData() as LoadedData | null

    if (!loadedData) return <Navigate to="/" replace/>


    const changeFilterRadio: ChangeEventHandler<HTMLInputElement> = (e) => {
        const value = e.target.value as QualityTag;
        if (value === QualityTag.NONE) {
            setFilterFunc(() => (_: ImageData) => true)
        } else {
            setFilterFunc(() => {
                return (data: ImageData) => {
                    console.log(`${data.qualityTag} ${value}`)
                    return data.qualityTag === value;
                };
            })
        }
        setFilter(value as QualityTag)
    }

    const images: (ReactImageGalleryItem & ImageData)[] = loadedData.images.map(value => {
        return {
            original: value.url,
            thumbnail: value.url,
            description: value.qualityTag,
            ...value
        }
    })

    return <div className="Result">
        <div className="filter-container">
            <MyInput filter={QualityTag.ANIMAL} filterState={filter} onChangeFunc={changeFilterRadio}/>
            <MyInput filter={QualityTag.EMPTY} filterState={filter} onChangeFunc={changeFilterRadio}/>
            <MyInput filter={QualityTag.BROKEN} filterState={filter} onChangeFunc={changeFilterRadio}/>
        </div>
        <ImageGallery items={images.filter(filterFunc)} lazyLoad thumbnailPosition="left"/>
    </div>;
}