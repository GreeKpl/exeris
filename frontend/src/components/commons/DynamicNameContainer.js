import {connect} from "react-redux";
import {getDynamicName, fromDynamicNamesState} from "../../modules/dynamicNames";
import {requestCharacterDetails} from "../../modules/details";
import React from "react";
import "./style.scss";

class DynamicName extends React.Component {
  render() {
    return <span className="DynamicName-clickable" onClick={this.props.onClick}>
      {this.props.name}
      </span>;
  }
}

export {DynamicName};

const mapStateToProps = (state, ownProps) => {
  return {
    observerId: ownProps.observerId,
    entityId: ownProps.entityId,
    name: getDynamicName(fromDynamicNamesState(state, ownProps.observerId), ownProps.entityId),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onClick: event => {
      dispatch(requestCharacterDetails(ownProps.observerId, ownProps.entityId));
    },
  }
};

const DynamicNameContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(DynamicName);

export default DynamicNameContainer;
