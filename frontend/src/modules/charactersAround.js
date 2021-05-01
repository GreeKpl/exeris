import * as Immutable from "immutable";
import {characterReducerDecorator} from "../util/characterReducerDecorator";
import {extractActionsFromHtml} from "../util/parseDynamicName";
import {addEntityInfo} from "./entities";

export const UPDATE_CHARACTERS_LIST = "exeris-front/charactersAround/UPDATE_CHARACTERS_LIST";

export const requestCharactersAround = (characterId) => {
  return (dispatch, getState, socket) => {
    socket.request("character.get_all_characters_around", characterId, charactersList => {
      charactersList.map(characterInfo => {
        dispatch(addEntityInfo(characterId, characterInfo));
        const actionsToUpdateNames = extractActionsFromHtml(characterId, characterInfo.name);
        actionsToUpdateNames.forEach(action => dispatch(action));
      });
      dispatch(updateCharactersAround(characterId, charactersList.map(characterInfo => characterInfo.id)));
    });
  }
};

export const updateCharactersAround = (characterId, characterIdsList) => {
  return {
    type: UPDATE_CHARACTERS_LIST,
    characterIdsList: characterIdsList,
    characterId: characterId,
  };
};


export const charactersAroundReducer = (state = Immutable.List(), action) => {
  switch (action.type) {
    case UPDATE_CHARACTERS_LIST:
      return Immutable.fromJS(action.characterIdsList);
    default:
      return state;
  }
};

export const decoratedCharactersAroundReducer = characterReducerDecorator(charactersAroundReducer);

export const getIdsOfCharactersAround = state => state;

export const fromCharactersAroundState = (state, characterId) =>
  state.getIn(["charactersAround", characterId], Immutable.List());
