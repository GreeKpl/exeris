import {applyMiddleware, compose, createStore} from "redux";
import thunk from "redux-thunk";
import {browserHistory} from "react-router";
import makeRootReducer from "./mainReducer";
import {updateLocation} from "./location";
import {responsiveStoreEnhancer} from "redux-responsive";
import socket from "../util/server";

export default (socket) => {
  // ======================================================
  // Middleware Configuration
  // ======================================================
  const middleware = [thunk.withExtraArgument(socket)];

  // ======================================================
  // Store Enhancers
  // ======================================================
  const enhancers = [responsiveStoreEnhancer];

  let composeEnhancers = compose;

  // ======================================================
  // Store Instantiation and HMR Setup
  // ======================================================
  const store = createStore(
    makeRootReducer,
    composeEnhancers(
      applyMiddleware(...middleware),
      ...enhancers
    )
  );
  store.asyncReducers = {};

  // To unsubscribe, invoke `store.unsubscribeHistory()` anytime
  store.unsubscribeHistory = browserHistory.listen(updateLocation(store));

  if (module.hot) {
    module.hot.accept('./mainReducer', () => {
      const reducers = require('./mainReducer').default;
      store.replaceReducer(reducers(store.asyncReducers))
    })
  }

  return store
}
