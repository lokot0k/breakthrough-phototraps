import {LoaderFunctionArgs, Navigate, useLoaderData} from "react-router-dom";
import ImageGallery, {ReactImageGalleryItem} from "react-image-gallery";
import {useState} from "react";

type QualityTag = "good" | "so-so" | "bad"

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
            {url: "/image1.jpg", qualityTag: "good"},
            {url: "/image2.jpg", qualityTag: "so-so"},
            {url: "/image3.jpg", qualityTag: "bad"},
        ].concat(Array(200).fill({url: "/image1.jpg", qualityTag: "good"})) as ImageData[],
        archives: {
            good: "archive_good.zip",
            "so-so": "archive_so-so.zip",
            bad: "archive_bad.zip",
        },
    }
}

export function Result() {
    const loadedData = useLoaderData() as LoadedData | null

    if (!loadedData) return <Navigate to="/" replace/>


    const images: ReactImageGalleryItem[] = loadedData.images.map(value => {
        return {
            original: value.url,
            thumbnail: value.url,
            description: value.qualityTag,
        }
    })

    return <div className="Result"><ImageGallery items={images} lazyLoad thumbnailPosition="left"/></div>;
}