import * as Immutable from "immutable";
import socket from "../util/server";
import {characterReducerDecorator} from "../util/characterReducerDecorator";
import {extractActionsFromHtml} from "../util/parseDynamicName";

export const APPLY_PANEL_CHANGE = "exeris-front/topPanel/APPLY_PANEL_CHANGE";
export const CLOSE_TOP_PANEL = "exeris-front/topPanel/CLOSE_TOP_PANEL";
export const ADD_MODIFIER = "exeris-front/topPanel/ADD_MODIFIER";
export const REMOVE_MODIFIER = "exeris-front/topPanel/REMOVE_MODIFIER";


export const DETAILS_CHARACTER = "DETAILS_CHARACTER";
export const DETAILS_COMBAT = "DETAILS_COMBAT";


export const requestCharacterDetails = (characterId, targetId) => {
  return dispatch => {
    socket.request("character.get_character_details", characterId, targetId, data => {
      const actionsToUpdateNames = extractActionsFromHtml(characterId, data.name);
      actionsToUpdateNames.forEach(action => dispatch(action));
      dispatch(applyCharacterDetails(characterId, data));
    });
  }
};

export const applyCharacterDetails = (characterId, data) => {
  return {
    type: APPLY_PANEL_CHANGE,
    panelType: DETAILS_CHARACTER,
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
    type: APPLY_PANEL_CHANGE,
    characterId: characterId,
    panelType: DETAILS_COMBAT,
    data: data,
  };
};


const addPanelModifier = (characterId, key, value) => {
  return {
    type: ADD_MODIFIER,
    characterId: characterId,
    key: key,
    value: value,
  }
};

const removePanelModifier = (characterId, key) => {
  return {
    type: REMOVE_MODIFIER,
    characterId: characterId,
    key: key,
  }
};

export const closeTopPanel = (characterId) => {
  return {
    type: CLOSE_TOP_PANEL,
    characterId: characterId,
  };
};


export const submitEditedName = (characterId, newName) => {
  return (dispatch, getState) => {
    const detailsData = getDetailsData(fromTopPanelState(getState(), characterId));
    const targetId = detailsData.get("id");
    socket.request("character.rename_entity", characterId, targetId, newName, () => {
      // panel is *probably* still open, so refresh it
      dispatch(requestCharacterDetails(characterId, targetId));
    });
  };
};


export const topPanelReducer = (state = Immutable.fromJS({
  type: null,
}), action) => {
  switch (action.type) {
    case CLOSE_TOP_PANEL:
      return Immutable.Map({
        type: null,
      });
    case APPLY_PANEL_CHANGE:
      return Immutable.fromJS(action.data).set("type", action.panelType);
    case ADD_MODIFIER:
      return state.set(action.key, action.value);
    case REMOVE_MODIFIER:
      return state.delete(action.key);
    default:
      return state;
  }
};

export const decoratedTopPanelReducer = characterReducerDecorator(topPanelReducer);

export const getDetailsType = state => state.get("type", null);

export const getDetailsData = state => state.delete("type");

export const fromTopPanelState = (state, characterId) => state.getIn(["topPanel", characterId], Immutable.Map());
