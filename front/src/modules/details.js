import * as Immutable from "immutable";
import socket from "../util/server";
import {characterReducerDecorator} from "../util/characterReducerDecorator";
import {extractActionsFromHtml} from "../util/parseDynamicName";
import {addEntityInfo} from "../modules/entities";

export const APPLY_DETAILS_CHANGE = "exeris-front/details/APPLY_DETAILS_CHANGE";
export const CLOSE_DETAILS = "exeris-front/details/CLOSE_DETAILS";
export const ADD_MODIFIER = "exeris-front/details/ADD_MODIFIER";
export const REMOVE_MODIFIER = "exeris-front/details/REMOVE_MODIFIER";


export const PANEL_CHARACTER = "PANEL_CHARACTER";
export const PANEL_COMBAT = "PANEL_COMBAT";
export const DIALOG_READABLE = "DIALOG_READABLE";


export const requestCharacterDetails = (characterId, targetId) => {
  return dispatch => {
    socket.request("character.get_character_details", characterId, targetId, entityInfo => {
      const actionsToUpdateNames = extractActionsFromHtml(characterId, entityInfo.name);
      actionsToUpdateNames.forEach(action => dispatch(action));
      dispatch(addEntityInfo(characterId, entityInfo));
    });
    dispatch(applyCharacterDetails(characterId, targetId));
  }
};

export const applyCharacterDetails = (characterId, targetId) => {
  return {
    type: APPLY_DETAILS_CHANGE,
    panelType: PANEL_CHARACTER,
    characterId: characterId,
    targetId: targetId,
  };
};

export const requestCombatDetails = (characterId, combatId) => {
  return dispatch => {
    socket.request("character.get_combat_details", characterId, combatId, combatInfo => {
      dispatch(addEntityInfo(characterId, combatInfo));
    });
    dispatch(applyCombatDetails(characterId, combatId));
  }
};

export const applyCombatDetails = (characterId, targetId) => {
  return {
    type: APPLY_DETAILS_CHANGE,
    characterId: characterId,
    panelType: PANEL_COMBAT,
    targetId: targetId,
  };
};


const addDetailsModifier = (characterId, key, value) => {
  return {
    type: ADD_MODIFIER,
    characterId: characterId,
    key: key,
    value: value,
  }
};

const removeDetailsModifier = (characterId, key) => {
  return {
    type: REMOVE_MODIFIER,
    characterId: characterId,
    key: key,
  }
};

export const closeDetails = (characterId) => {
  return {
    type: CLOSE_DETAILS,
    characterId: characterId,
  };
};


export const submitEditedName = (characterId, newName) => {
  return (dispatch, getState) => {
    const targetId = getDetailsTarget(fromDetailsState(getState(), characterId));
    socket.request("character.rename_entity", characterId, targetId, newName, () => {
      // panel is *probably* still open, so refresh it
      dispatch(requestCharacterDetails(characterId, targetId));
    });
  };
};


export const detailsReducer = (state = Immutable.fromJS({
  type: null,
}), action) => {
  switch (action.type) {
    case CLOSE_DETAILS:
      return Immutable.Map({
        type: null,
      });
    case APPLY_DETAILS_CHANGE:
      return Immutable.Map({
        "type": action.panelType,
        "targetId": action.targetId,
      });
    case ADD_MODIFIER:
      return state.set(action.key, action.value);
    case REMOVE_MODIFIER:
      return state.delete(action.key);
    default:
      return state;
  }
};

export const decoratedDetailsReducer = characterReducerDecorator(detailsReducer);

export const getDetailsType = state => state.get("type", null);

export const getDetailsTarget = state => state.get("targetId", null);

export const fromDetailsState = (state, characterId) => state.getIn(["details", characterId], Immutable.Map());
