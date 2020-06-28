import {applyMiddleware, compose, createStore} from "redux";
import thunk from "redux-thunk";
import makeRootReducer from "./mainReducer";
import {responsiveStoreEnhancer} from "redux-responsive";

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

  if (module.hot) {
    module.hot.accept('./mainReducer', () => {
      const reducers = require('./mainReducer').default;
      store.replaceReducer(reducers())
    })
  }

  return store
}
