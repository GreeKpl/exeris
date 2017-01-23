import React, {Component, PropTypes} from "react";
import {browserHistory, Router} from "react-router";
import {Provider} from "react-redux";
import * as duckModules from "../modules";

class AppContainer extends Component {

  static shouldComponentUpdate() {
    return false;
  }

  componentDidMount() {
    for (let module of Object.values(duckModules)) {
      if ("setUpSocketioListeners" in module) {
        module.setUpSocketioListeners(this.props.store.dispatch);
      }
    }
  }

  render() {
    const {routes, store} = this.props;

    return (
      <Provider store={store}>
        <Router history={browserHistory} children={routes}/>
      </Provider>
    )
  }
}

AppContainer.propTypes = {
  routes: PropTypes.object.isRequired,
  store: PropTypes.object.isRequired,
};

export default AppContainer
