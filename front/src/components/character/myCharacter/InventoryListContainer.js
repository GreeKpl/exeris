import {connect} from "react-redux";
import InventoryList from "./InventoryList";
import {
  requestInventoryEntities,
  fromEntitiesState,
  getEntityInfos,
  getChildren,
  getExpanded,
  getSelectedEntities,
  collapseEntity,
  expandEntity,
  selectEntity,
  deselectEntity,
  getItemsInInventory,
  clearEntitySelection
} from "../../../modules/entities";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    itemsInInventory: getItemsInInventory(fromEntitiesState(state, ownProps.characterId)),
    info: getEntityInfos(fromEntitiesState(state, ownProps.characterId)),
    children: getChildren(fromEntitiesState(state, ownProps.characterId)),
    expanded: getExpanded(fromEntitiesState(state, ownProps.characterId)),
    selectedEntities: getSelectedEntities(fromEntitiesState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    requestState: () => dispatch(requestInventoryEntities(ownProps.characterId)),
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
  };
};


const InventoryListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(InventoryList);

export default InventoryListContainer;
