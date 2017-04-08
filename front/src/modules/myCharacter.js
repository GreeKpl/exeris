import * as Immutable from "immutable";
import {characterReducerDecorator} from "../util/characterReducerDecorator";
import socket from "../util/server";
import {addEntityInfo, getEntityInfo, fromEntitiesState} from "./entities";

export const UPDATE_MY_CHARACTER_ID = "exeris-front/myCharacter/UPDATE_MY_CHARACTER_ID";


export const requestMyCharacterInfo = characterId => {
  return dispatch => {
    socket.request("character.get_my_character_info", characterId, characterInfo => {
      dispatch(updateMyCharacterState(characterId, characterInfo.id));
      dispatch(addEntityInfo(characterId, characterInfo));
    });
  }
};

export const updateMyCharacterState = (characterId, myCharacterEntityId) => {
  return {
    type: UPDATE_MY_CHARACTER_ID,
    characterId: characterId,
    myCharacterEntityId: myCharacterEntityId,
  };
};

export const myCharacterReducer = (state = Immutable.fromJS({
  myCharacterEntityId: null,
}), action) => {
  switch (action.type) {
    case UPDATE_MY_CHARACTER_ID:
      return Immutable.fromJS({
        myCharacterEntityId: action.myCharacterEntityId,
      });
    default:
      return state;
  }
};

export const decoratedMyCharacterReducer = characterReducerDecorator(myCharacterReducer);

export const getMyCharacterEntityId = state => state.get("myCharacterEntityId", null);

export const getMyCharacterInfoFromMyCharacterState = (state, characterId) => {
  const myCharacterState = fromMyCharacterState(state, characterId);
  const myCharacterEntityId = myCharacterState.get("myCharacterEntityId", null);
  return getEntityInfo(myCharacterEntityId, fromEntitiesState(state, characterId));
};

export const fromMyCharacterState = (state, characterId) =>
  state.getIn(["myCharacter", characterId], Immutable.Map());
