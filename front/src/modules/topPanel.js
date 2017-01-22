import * as Immutable from "immutable";
import socket from "../util/server";
import {characterReducerDecorator} from "../util/characterReducerDecorator";

export const APPLY_CHARACTER_DETAILS = "exeris-front/topPanel/APPLY_CHARACTER_DETAILS";
export const APPLY_COMBAT_DETAILS = "exeris-front/topPanel/APPLY_COMBAT_DETAILS";
export const CLOSE_TOP_PANEL = "exeris-front/topPanel/CLOSE_TOP_PANEL";

export const DETAILS_CHARACTER = "DETAILS_CHARACTER";
export const DETAILS_COMBAT = "DETAILS_COMBAT";


export const requestCharacterDetails = (characterId, targetId) => {
  return dispatch => {
    socket.request("character.get_character_details", characterId, targetId, data => {
      dispatch(applyCharacterDetails(characterId, data));
    });
  }
};

export const applyCharacterDetails = (characterId, data) => {
  return {
    type: APPLY_CHARACTER_DETAILS,
    characterId: characterId,
    data: data,
  };
};

export const requestCombatDetails = (characterId, combatId) => {
  return dispatch => {
    socket.request("character.get_combat_details", characterId, combatId, data => {
      dispatch(applyCombatDetails(characterId, data));
    });
  }
};

export const applyCombatDetails = (characterId, data) => {
  return {
    type: APPLY_COMBAT_DETAILS,
    characterId: characterId,
    data: data,
  };
};

export const closeTopPanel = (characterId) => {
  return {
    type: CLOSE_TOP_PANEL,
    characterId: characterId,
  };
};


export const topPanelReducer = (state = Immutable.fromJS({
  type: null,
}), action) => {
  switch (action.type) {
    case CLOSE_TOP_PANEL:
      return Immutable.Map({type: null});
    case APPLY_CHARACTER_DETAILS:
      return Immutable.fromJS(action.data).set("type", DETAILS_CHARACTER);
    case APPLY_COMBAT_DETAILS:
      return Immutable.fromJS(action.data).set("type", DETAILS_COMBAT);
    default:
      return state;
  }
};

export const decoratedTopPanelReducer = characterReducerDecorator(topPanelReducer);

export const getDetailsType = state => state.get("type");

export const getDetailsData = state => state.delete("type");

export const fromTopPanelState = (state, characterId) => state.getIn(["topPanel", characterId], Immutable.Map());
