import React, {useEffect, useState} from "react";
import PropTypes from "prop-types";
import {browserHistory, Router} from "react-router";
import {Provider} from "react-redux";
import * as duckModules from "../modules";
import {I18nextProvider} from 'react-i18next';
import i18n from "../i18n";
import setupSocketio from "../util/server";
import createStore from "../store/createStore";
import routes from "./routes";

const AppContainer = () => {
  const [store, setStore] = useState(null);

  useEffect(() => {
    const socket = setupSocketio();
    const store = createStore(socket);
    for (let module of Object.values(duckModules)) {
      if ("setUpSocketioListeners" in module) {
        module.setUpSocketioListeners(store.dispatch, socket);
      }
    }
    setStore(store);
  }, []);

  if (!store) {
    return null;
  }

  return (
    <I18nextProvider i18n={i18n}>
      <Provider store={store}>
        <Router history={browserHistory} children={routes}/>
      </Provider>
    </I18nextProvider>
  )
};

export default AppContainer
