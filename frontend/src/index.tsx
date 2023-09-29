import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import Welcome from './Welcome';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-image-gallery/styles/scss/image-gallery.scss'
import 'react-image-gallery/styles/css/image-gallery.css'
import {createBrowserRouter, RouterProvider} from "react-router-dom";
import {Result, loader as resultLoader} from "./Result";

const router = createBrowserRouter([
    {
        path: "/",
        element: <Welcome/>,
    },
    {
        path: "/result",
        element: <Result/>,
        loader: resultLoader
    }
])

const root = ReactDOM.createRoot(
    document.getElementById('root') as HTMLElement
);

root.render(
    <React.StrictMode>
        <RouterProvider router={router}/>
    </React.StrictMode>
);
