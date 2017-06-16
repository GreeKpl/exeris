import * as Immutable from "immutable";

export const UPDATE_LIST_OF_ENTITY_TYPES = "exeris-front/gameContent/UPDATE_LIST_OF_ENTITY_TYPES";
export const SELECT_ENTITY_TYPE = "exeris-front/gameContent/SELECT_ENTITY_TYPE";
export const CREATE_ENTITY_TYPE = "exeris-front/gameContent/CREATE_ENTITY_TYPE";


export const CLASSES = {
  ENTITY_BASE: "base",
  ENTITY_ITEM: "item",
  ENTITY_LOCATION: "location",
  ENTITY_ROOT_LOCATION: "root_location",
  ENTITY_PASSAGE: "passage",
  ENTITY_CHARACTER: "character",
  ENTITY_ACTIVITY: "activity",
  ENTITY_TERRAIN_AREA: "terrain_area",
  ENTITY_GROUP: "group",
  ENTITY_COMBAT: "combat",
  ENTITY_BURIED_CONTENT: "buried_content",
};

export const requestAllEntityTypes = () => {
  return (dispatch, getState, socket) => {
    socket.request("admin.get_all_entity_types", entityTypes => {
      dispatch(updateListOfEntityTypes(entityTypes));
    });
  };
};

export const requestEntityType = entityTypeName => {
  return (dispatch, getState, socket) => {
    socket.request("admin.get_entity_type", entityTypeName, entityType => {
      dispatch(openEntityTypeForm(entityType));
    });
  };
};

export const openEntityTypeForm = entityType => {
  return {
    type: SELECT_ENTITY_TYPE,
    entityType,
  };
};

export const closeEntityTypeForm = () => {
  return {
    type: SELECT_ENTITY_TYPE,
    entityType: null,
  }
};

export const requestUpdateEntityType = entityType => {
  return (dispatch, getState, socket) => {
    socket.request("admin.update_entity_type", entityType, () => {
      dispatch(closeEntityTypeForm());
    });
  };
};

export const requestCreateNewEntityType = newEntityType => {
  return (dispatch, getState, socket) => {
    socket.request("admin.create_entity_type", newEntityType, () => {
      dispatch(closeEntityTypeForm());
    });
  };
};

export const updateListOfEntityTypes = entityTypes => {
  return {
    type: UPDATE_LIST_OF_ENTITY_TYPES,
    entityTypes,
  };
};

export const gameContentReducer = (state = Immutable.fromJS({entityTypes: []}), action) => {
  switch (action.type) {
    case UPDATE_LIST_OF_ENTITY_TYPES:
      return state.set("entityTypes", Immutable.fromJS(action.entityTypes));
    case SELECT_ENTITY_TYPE:
      return state.set("selectedEntityType", Immutable.fromJS(action.entityType))
        .set("newEntityType", false);
    case CREATE_ENTITY_TYPE:
      return state.set("selectedEntityType", Immutable.fromJS(action.entityType))
        .set("newEntityType", false);
    default:
      return state;
  }
};

export const getAllEntityTypes = state => state.get("entityTypes", []);

export const getSelectedEntityType = state => state.get("selectedEntityType", null);

export const isNewEntityType = state => state.get("newEntityType", false);

export const fromGameContentState = state => state.get("gameContent", Immutable.Map());
