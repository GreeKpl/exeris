import {CLASSES, getSelectedEntityType, fromGameContentState} from "../../../modules/gameContent";
import React from "react";
import {connect} from "react-redux";

const EntityTypeForm = ({typeParams}) => {
  switch (typeParams.get("class")) {
    case CLASSES.ENTITY_ITEM:
      return <ItemTypeForm typeParams={typeParams}/>;
    default:
      return <div>Unsupported entity class</div>;
  }
};


const mapEntityStateToProps = (state) => {
  const selectedEntityType = getSelectedEntityType(fromGameContentState(state));
  return {
    typeParams: selectedEntityType,
    selectedEntityTypeName: selectedEntityType ? selectedEntityType.get("name") : null,
  };
};

const mapEntityDispatchToProps = (dispatch) => {
  return {};
};

const EntityTypeFormContainer = connect(
  mapEntityStateToProps,
  mapEntityDispatchToProps
)(EntityTypeForm);


export default EntityTypeFormContainer;


const ItemTypeForm = ({typeParams}) => {
  return <div>Item type placeholder {JSON.stringify(typeParams.toJS())}</div>;
};
