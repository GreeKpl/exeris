import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';

export const createMockStore = (initialState, mapOfParamsForCallback) => {
  const socketMock = requestMock(mapOfParamsForCallback);
  const mockStore = configureMockStore([thunk.withExtraArgument(socketMock)]);
  return mockStore(initialState);
};

export const requestMock = (mapOfParamsForCallback) => {
  return {
    request: (eventName, ...requestArgs) => {
      let paramsForCallback;
      if (Array.isArray(mapOfParamsForCallback)) {
        paramsForCallback = mapOfParamsForCallback;
      } else {
        paramsForCallback = mapOfParamsForCallback[eventName];
      }

      const callback = [...requestArgs].pop();
      callback(...paramsForCallback);
    }
  };
};
