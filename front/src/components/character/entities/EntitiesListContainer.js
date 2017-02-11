import {connect} from "react-redux";
import EntitiesList from "./EntitiesList";
import {
  requestRootEntities,
  getChildren,
  getEntityInfos,
  getRootEntities,
  getExpanded,
  fromEntitiesState,
  expandEntity,
  collapseEntity,
  selectEntity,
  deselectEntity,
  clearEntitySelection,
  getSelectedEntities
} from "../../../modules/entities";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    rootEntities: getRootEntities(fromEntitiesState(state, ownProps.characterId)),
    info: getEntityInfos(fromEntitiesState(state, ownProps.characterId)),
    children: getChildren(fromEntitiesState(state, ownProps.characterId)),
    expanded: getExpanded(fromEntitiesState(state, ownProps.characterId)),
    selectedEntities: getSelectedEntities(fromEntitiesState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    requestState: () => dispatch(requestRootEntities(ownProps.characterId)),
    clearSelection: () => dispatch(clearEntitySelection(ownProps.characterId)),
    onExpand: entity => {
      dispatch(expandEntity(ownProps.characterId, entity));
    },
    onCollapse: entity => {
      dispatch(collapseEntity(ownProps.characterId, entity));
    },
    onSelect: entity => {
      dispatch(selectEntity(ownProps.characterId, entity));
    },
    onDeselect: entity => {
      dispatch(deselectEntity(ownProps.characterId, entity));
    },
  }
};

const EntitiesListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EntitiesList);

export default EntitiesListContainer;
