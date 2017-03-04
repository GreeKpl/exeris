import * as Immutable from "immutable";
import socket from "../util/server";
import {characterReducerDecorator} from "../util/characterReducerDecorator";
import {extractActionsFromHtml} from "../util/parseDynamicName";

export const UPDATE_CHARACTERS_LIST = "exeris-front/charactersAround/UPDATE_CHARACTERS_LIST";

export const requestCharactersAround = (characterId) => {
  return dispatch => {
    socket.request("character.get_all_characters_around", characterId, charactersList => {
      charactersList.map(characterInfo => {
        const actionsToUpdateNames = extractActionsFromHtml(characterId, characterInfo.name);
        actionsToUpdateNames.forEach(action => dispatch(action));
      });
      dispatch(updateCharactersAround(characterId, charactersList));
    });
  }
};

export const updateCharactersAround = (characterId, charactersList) => {
  return {
    type: UPDATE_CHARACTERS_LIST,
    charactersList: charactersList,
    characterId: characterId,
  };
};


export const charactersAroundReducer = (state = Immutable.List(), action) => {
  switch (action.type) {
    case UPDATE_CHARACTERS_LIST:
      return Immutable.fromJS(action.charactersList);
    default:
      return state;
  }
};

export const decoratedCharactersAroundReducer = characterReducerDecorator(charactersAroundReducer);

export const getCharactersAround = state => state;

export const getCombatName = state => state.get("combatName");

export const getCombatId = state => state.get("combatId");

export const fromCharactersAroundState = (state, characterId) =>
  state.getIn(["charactersAround", characterId], Immutable.List());
