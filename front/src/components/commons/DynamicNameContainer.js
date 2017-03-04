import DynamicName from "./DynamicName";
import {connect} from "react-redux";
import {getDynamicName, fromDynamicNamesState} from "../../modules/dynamicNames";
import {requestCharacterDetails} from "../../modules/topPanel";

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
