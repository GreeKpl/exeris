import {connect} from "react-redux";
import {
  clearEntitySelection,
  collapseEntity,
  deselectEntity,
  expandEntity,
  fromEntitiesState,
  getChildren,
  getEntityInfos,
  getExpanded,
  getItemsInInventory,
  getSelectedEntities,
  requestInventoryEntities,
  selectEntity
} from "../../../modules/entities";
import React from "react";
import Entities from "../../commons/entities/Entities";
import {Card} from "react-bootstrap";

export class InventoryList extends React.Component {
  componentDidMount() {
    this.props.requestState();
    this.props.clearSelection();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.characterId !== this.props.characterId) {
      this.props.requestState();
    }
  }

  render() {
    return (
      <Card>
        <Card.Header>Inventory</Card.Header>
        <Card.Body>
          <Entities entities={this.props.itemsInInventory} {...this.props}/>
        </Card.Body>
      </Card>
    );
  }
}


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
