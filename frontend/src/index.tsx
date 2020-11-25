import React from 'react';
import ReactDOM from 'react-dom';
import AppContainer from './app/AppContainer';
import * as serviceWorker from './serviceWorker';
import 'bootstrap/dist/css/bootstrap.css';
import {createBrowserHistory} from "history";
import setupSocketio from "./util/server";
import createStore from "./store/createStore";

const history = createBrowserHistory();
const socket = setupSocketio();
const store = createStore(socket);

ReactDOM.render(
  <React.StrictMode>
    <AppContainer/>
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
