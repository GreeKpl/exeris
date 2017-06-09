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
  mockStore.socketCalledWith = mockStore.socketCalledWith.bind(mockStore);
  return mockStore;
};

export const requestMock = (mapOfParamsForCallback) => {
  const socketRequestMock = {
    calls: [],
    request: function (eventName, ...requestArgs) {
      let paramsForCallback;
      if (Array.isArray(mapOfParamsForCallback) || mapOfParamsForCallback === null) {
        paramsForCallback = mapOfParamsForCallback;
      } else {
        paramsForCallback = mapOfParamsForCallback[eventName];
      }

      // if there are arguments, then callback exists and it needs to be called
      const requestArgsWithoutCallback = [...requestArgs];
      if (paramsForCallback !== null) {
        const callback = requestArgsWithoutCallback.pop();
        callback(...paramsForCallback);
      }
      this.calls.push([eventName, ...requestArgsWithoutCallback]);
    }
  };
  socketRequestMock.request = socketRequestMock.request.bind(socketRequestMock);
  return socketRequestMock;
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
