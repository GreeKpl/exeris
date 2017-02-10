import * as Immutable from "immutable";
import socket from "../util/server";
import {characterReducerDecorator} from "../util/characterReducerDecorator";

export const ADD_ENTITY_INFO = "exeris-front/entities/ADD_ENTITY_INFO";
export const UPDATE_ROOT_ENTITIES_LIST = "exeris-front/entities/UPDATE_ROOT_ENTITIES_LIST";
export const UPDATE_ITEMS_IN_INVENTORY_LIST = "exeris-front/entities/UPDATE_ITEMS_IN_INVENTORY_LIST";

export const UPDATE_CHILDREN_OF_ENTITY = "exeris-front/entities/UPDATE_CHILDREN_OF_ENTITY";
export const REMOVE_CHILD_OF_ENTITY = "exeris-front/entities/REMOVE_CHILD_OF_ENTITY";

export const EXPAND_ENTITY = "exeris-front/entities/EXPAND_ENTITY";
export const COLLAPSE_ENTITY = "exeris-front/entities/COLLAPSE_ENTITY";
export const SELECT_ENTITY = "exeris-front/entities/SELECT_ENTITY";
export const DESELECT_ENTITY = "exeris-front/entities/DESELECT_ENTITY";

export const SELECT_ENTITY_ACTION = "exeris-front/entities/SELECT_ENTITY_ACTION";


export const requestRefreshEntity = (characterId, entityId) => {
  return (dispatch, getState) => {
    const childrenByEntity = getChildren(fromEntitiesState(getState(), characterId));
    const parentEntities = childrenByEntity.filter(children => children.includes(entityId)).keySeq();
    if (!parentEntities.size) {
      return; // this entity is not visible anywhere
    }

    const parentId = parentEntities.first();
    socket.request("character.get_extended_entity_info", characterId, entityId, parentId, extendedEntityInfo => {
      if (extendedEntityInfo.info) {
        dispatch(addEntityInfo(characterId, extendedEntityInfo.info));
        dispatch(updateChildrenOfEntity(characterId, entityId, extendedEntityInfo.children));
      } else {
        dispatch(removeChildOfEntity(characterId, parentId, extendedEntityInfo.id));
      }
    });
  };
};

export const requestRootEntities = (characterId) => {
  return dispatch => {
    socket.request("character.get_root_entities", characterId, entitiesInfo => {
      for (let entityInfo of entitiesInfo) {
        dispatch(addEntityInfo(characterId, entityInfo));
      }

      const entitiesIds = entitiesInfo.map(info => info.id);
      dispatch(updateRootEntitiesList(characterId, entitiesIds));
    });
  }
};

export const requestInventoryEntities = characterId => {
  return dispatch => {
    socket.request("character.get_items_in_inventory", characterId, entitiesInfo => {
      for (let entityInfo of entitiesInfo) {
        dispatch(addEntityInfo(characterId, entityInfo));
      }

      const entitiesIds = entitiesInfo.map(info => info.id);
      dispatch(updateItemsInInventoryList(characterId, entitiesIds));
    });
  }
};

const getParentEntity = (characterId, entityId, state) => {
  const children = getChildren(fromEntitiesState(state, characterId));
  const keys = children.filter((value, key) => value.includes(entityId)).keys();
  if (keys.size > 0) {
    return keys.first();
  }
  return null;
};

export const requestChildrenEntities = (characterId, entityId) => {
  return (dispatch, getState) => {
    const parentEntity = getParentEntity(characterId, entityId, getState());

    socket.request("character.get_children_entities", characterId, entityId, parentEntity, childrenInfo => {
      for (let entityInfo of childrenInfo) {
        dispatch(addEntityInfo(characterId, entityInfo));
      }

      const childrenIds = childrenInfo.map(info => info.id);
      dispatch(updateChildrenOfEntity(characterId, entityId, childrenIds));
    });
  }
};

export const addEntityInfo = (characterId, entityInfo) => {
  return {
    type: ADD_ENTITY_INFO,
    entityInfo: entityInfo,
    characterId: characterId,
  };
};

export const expandEntity = (characterId, entityId) => {
  return dispatch => {
    dispatch({
      type: EXPAND_ENTITY,
      entityId: entityId,
      characterId: characterId,
    });

    dispatch(requestChildrenEntities(characterId, entityId));
  }
};


export const collapseEntity = (characterId, entityId) => {
  return dispatch => {
    dispatch({
      type: COLLAPSE_ENTITY,
      entityId: entityId,
      characterId: characterId,
    });
  }
};

export const selectEntity = (characterId, entityId) => {
  return dispatch => {
    dispatch({
      type: SELECT_ENTITY,
      entityId: entityId,
      characterId: characterId,
    });

    dispatch(requestChildrenEntities(characterId, entityId));
  }
};


export const deselectEntity = (characterId, entityId) => {
  return dispatch => {
    dispatch({
      type: DESELECT_ENTITY,
      entityId: entityId,
      characterId: characterId,
    });
  }
};

export const updateRootEntitiesList = (characterId, rootEntitiesList) => {
  return {
    type: UPDATE_ROOT_ENTITIES_LIST,
    rootEntitiesList: rootEntitiesList,
    characterId: characterId,
  };
};


export const updateItemsInInventoryList = (characterId, itemsList) => {
  return {
    type: UPDATE_ITEMS_IN_INVENTORY_LIST,
    itemsList: itemsList,
    characterId: characterId,
  };
};

export const updateChildrenOfEntity = (characterId, parentEntityId, childrenIds) => {
  return {
    type: UPDATE_CHILDREN_OF_ENTITY,
    parentEntityId: parentEntityId,
    childrenIds: childrenIds,
    characterId: characterId,
  };
};


export const removeChildOfEntity = (characterId, parentEntityId, childId) => {
  return {
    type: REMOVE_CHILD_OF_ENTITY,
    parentEntityId: parentEntityId,
    childId: childId,
    characterId: characterId,
  };
};


export const selectEntityAction = (characterId, actionType, details) => {
  return {
    type: SELECT_ENTITY_ACTION,
    actionType: actionType,
    details: details,
    characterId: characterId,
  }
};

export const clearSelectedEntityAction = characterId => {
  return {
    type: SELECT_ENTITY_ACTION,
    actionType: null,
    details: {},
    characterId: characterId,
  };
};


export const entitiesReducer = (state = Immutable.fromJS(
  {
    "info": {},
    "children": {},
    "rootEntities": [],
    "itemsInInventory": [],
    "expanded": Immutable.Set(),
    "selected": Immutable.Set(),
    "actionType": null,
    "actionDetails": {},
  }), action) => {
  switch (action.type) {
    case ADD_ENTITY_INFO:
      const entityInfo = action.entityInfo;
      return state.setIn(["info", entityInfo.id], Immutable.fromJS(entityInfo));
    case UPDATE_CHILDREN_OF_ENTITY:
      return state.setIn(["children", action.parentEntityId],
        Immutable.fromJS(action.childrenIds));
    case REMOVE_CHILD_OF_ENTITY:
      return state.updateIn(["children", action.parentEntityId], Immutable.List(),
        list => list.filter(el => el !== action.childId));
    case UPDATE_ROOT_ENTITIES_LIST:
      return state.set("rootEntities", Immutable.fromJS(action.rootEntitiesList));
    case UPDATE_ITEMS_IN_INVENTORY_LIST:
      return state.set("itemsInInventory", Immutable.fromJS(action.itemsList));
    case EXPAND_ENTITY:
      return state.update("expanded", expandedSet => expandedSet.add(action.entityId));
    case COLLAPSE_ENTITY:
      return state.update("expanded", expandedSet => expandedSet.delete(action.entityId));
    case SELECT_ENTITY:
      return state.update("selected", selectedSet => selectedSet.add(action.entityId))
        .set("actionType", null)
        .set("actionDetails", Immutable.Map());
    case DESELECT_ENTITY:
      return state.update("selected", selectedSet => selectedSet.delete(action.entityId))
        .set("actionType", null)
        .set("actionDetails", Immutable.Map());
    case SELECT_ENTITY_ACTION:
      return state.set("actionType", action.actionType)
        .set("actionDetails", Immutable.fromJS(action.details));
    default:
      return state;
  }
};

export const decoratedEntitiesReducer = characterReducerDecorator(entitiesReducer);

export const getRootEntities = state => state.get("rootEntities", Immutable.List());

export const getItemsInInventory = state => state.get("itemsInInventory", Immutable.List());

export const getChildren = (state) => state.get("children", Immutable.Map());

export const getEntityInfos = (state) => state.get("info", Immutable.Map());

export const getExpanded = (state) => state.get("expanded", Immutable.Set());

export const getSelectedEntities = (state) => state.get("selected", Immutable.Set());

// entity actions
export const getActionType = (state) => state.get("actionType", null);

export const getActionDetails = (state) => state.get("actionDetails", Immutable.Map());

export const fromEntitiesState = (state, characterId) =>
  state.getIn(["entities", characterId], Immutable.Map());
