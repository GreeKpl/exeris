import React, {Component, PropTypes} from "react";
import {browserHistory, Router} from "react-router";
import {Provider} from "react-redux";
import * as duckModules from "../modules";
import {I18nextProvider} from 'react-i18next';
import i18n from "../i18n";
import socket from "../util/server";


class AppContainer extends Component {

  static shouldComponentUpdate() {
    return false;
  }

  componentDidMount() {
    for (let module of Object.values(duckModules)) {
      if ("setUpSocketioListeners" in module) {
        module.setUpSocketioListeners(this.props.store.dispatch, socket);
      }
    }
  }

  render() {
    const {routes, store} = this.props;

    return (
      <I18nextProvider i18n={i18n}>
        <Provider store={store}>
          <Router history={browserHistory} children={routes}/>
        </Provider>
      </I18nextProvider>
    )
  }
}

AppContainer.propTypes = {
  routes: PropTypes.object.isRequired,
  store: PropTypes.object.isRequired,
};

export default AppContainer
