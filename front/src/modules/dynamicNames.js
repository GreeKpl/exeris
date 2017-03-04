import * as Immutable from "immutable";
import {characterReducerDecorator} from "../util/characterReducerDecorator";

export const UPDATE_DYNAMIC_NAME = "exeris-front/dynamicNames/UPDATE_DYNAMIC_NAME";

export const updateDynamicName = (characterId, entityId, name) => {
  return {
    type: UPDATE_DYNAMIC_NAME,
    name: name,
    entityId: entityId,
    characterId: characterId,
  };
};


export const dynamicNamesReducer = (state = Immutable.Map(), action) => {
  switch (action.type) {
    case UPDATE_DYNAMIC_NAME:
      return state.set(action.entityId, action.name);
    default:
      return state;
  }
};

export const decoratedDynamicNamesReducer = characterReducerDecorator(dynamicNamesReducer);

export const getDynamicName = (state, entityId) => state.get(entityId, null);

export const fromDynamicNamesState = (state, characterId) =>
  state.getIn(["dynamicNames", characterId], Immutable.Map());
