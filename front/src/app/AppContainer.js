import React, {useEffect, useState} from "react";
import {Router} from "react-router";
import {createBrowserHistory} from 'history';
import {Provider} from "react-redux";
import * as duckModules from "../modules";
import {I18nextProvider} from 'react-i18next';
import i18n from "../i18n";
import setupSocketio from "../util/server";
import createStore from "../store/createStore";
import Root from "./Root";


const AppContainer = () => {
  const [store, setStore] = useState(null);
  const [history, setHistory] = useState(null);

  useEffect(() => {
    const socket = setupSocketio();
    const store = createStore(socket);
    for (let module of Object.values(duckModules)) {
      if ("setUpSocketioListeners" in module) {
        module.setUpSocketioListeners(store.dispatch, socket);
      }
    }
    setStore(store);
    setHistory(createBrowserHistory());
  }, []);

  if (!store || !history) {
    return null;
  }

  return (
    <I18nextProvider i18n={i18n}>
      <Provider store={store}>
        <Router history={history}>
          <Root/>
        </Router>
      </Provider>
    </I18nextProvider>
  )
};

export default AppContainer;
