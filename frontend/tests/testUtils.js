import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import deepEqual from "deep-equal";

export const createMockStore = (initialState, mapOfParamsForCallback) => {
  const socketMock = requestMock(mapOfParamsForCallback);
  const mockStoreFactory = configureMockStore([thunk.withExtraArgument(socketMock)]);
  const mockStore = mockStoreFactory(initialState);

  mockStore.socketCalledWith = (...expectedArgs) => {
    const matchedCalls = socketMock.calls.filter(calledArgs =>
      deepEqual(calledArgs, expectedArgs));

    if (matchedCalls.length === 0) {
      throw new Error("socketio request not called with args " + expectedArgs);
    }
  };
  mockStore.socketNotCalled = () => {
    if (socketMock.calls.length > 0) {
      throw new Error("socketio request should never be called, but it was called with args " + socketMock.calls);
    }
  };
  mockStore.socketCalledWith = mockStore.socketCalledWith.bind(mockStore);
  mockStore.socketNotCalled = mockStore.socketNotCalled.bind(mockStore);
  return mockStore;
};

export const requestMock = (mapOfParamsForCallback) => {
  const socketRequestMock = {
    calls: [],
    request: function (eventName, ...requestArgs) {
      let paramsForCallback = getParamsForCallback(mapOfParamsForCallback, eventName);

      // if there are arguments, then callback exists and it needs to be called
      const argsWithoutCallback = [...requestArgs];
      let callback = popCallbackFromArgsArray(argsWithoutCallback);
      if (paramsForCallback !== null) {
        if (callback !== null) {
          callback(...paramsForCallback);
        } else {
          throw new Error("Request '" + argsWithoutCallback[0]
            + "' should call a callback, but there is no callback for the request");
        }
      }
      this.calls.push([eventName, ...argsWithoutCallback]);
    }
  };
  socketRequestMock.request = socketRequestMock.request.bind(socketRequestMock);
  return socketRequestMock;
};

const getParamsForCallback = function (mapOfParamsForCallback, eventName) {
  if (Array.isArray(mapOfParamsForCallback) || mapOfParamsForCallback === null) {
    return mapOfParamsForCallback;
  } else {
    return mapOfParamsForCallback[eventName];
  }
};

const popCallbackFromArgsArray = function (argsWithoutCallback) {
  if (Object.prototype.toString.call(argsWithoutCallback[argsWithoutCallback.length - 1]) === '[object Function]') {
    return argsWithoutCallback.pop();
  }
  return null;
};

export class DependenciesStubber {
  constructor(__RewireAPI__, methods) {
    this.__RewireAPI__ = __RewireAPI__;
    this.methods = methods;
  }

  rewireAll() {
    for (let [methodName, stubFunction] of Object.entries(this.methods)) {
      this.__RewireAPI__.__Rewire__(methodName, stubFunction);
    }
  }

  unwireAll() {
    for (let methodName of Object.keys(this.methods)) {
      this.__RewireAPI__.__ResetDependency__(methodName);
    }
  }
}
