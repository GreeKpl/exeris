import {connect} from "react-redux";
import React from "react";
import {
  fromGameContentState, getAllEntityTypes, requestAllPropertyNames, getSelectedEntityType,
  requestAllEntityTypes, requestEntityType
} from "../../../modules/gameContent";
import {ListGroup, ListGroupItem} from "react-bootstrap";
import "./style.scss";
import EntityTypeFormContainer from "./EntityTypeForm";


class EntityTypeListRow extends React.Component {

  constructor(props) {
    super(props);

    this.handleClick = this.handleClick.bind(this);
  }

  handleClick() {
    this.props.onClick(this.props.displayedName);
  }

  render() {
    const {displayedEntityType, displayedName} = this.props;
    return <ListGroupItem key={displayedName}
                          onClick={this.handleClick}>
      {displayedName} - {displayedEntityType.get("class")}
    </ListGroupItem>;
  }
}

class EntityTypesManagement extends React.Component {
  componentDidMount() {
    this.props.requestState();
  }

  render() {
    return <div>
      <ListGroup className="EntityTypes-List">
        {this.props.entityTypes.map(displayedEntityType =>
          [<EntityTypeListRow displayedEntityType={displayedEntityType}
                              displayedName={displayedEntityType.get("name")}
                              onClick={this.props.onClick}
          />,
            (this.props.selectedEntityTypeName === displayedEntityType.get("name"))
            && <EntityTypeFormContainer/>
          ]
        )}
      </ListGroup>
    </div>;
  }
}

export {EntityTypesManagement};


const mapStateToProps = (state) => {
  const selectedEntityType = getSelectedEntityType(fromGameContentState(state));
  return {
    entityTypes: getAllEntityTypes(fromGameContentState(state)),
    selectedEntityTypeName: selectedEntityType ? selectedEntityType.get("name") : null,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    requestState: () => {
      dispatch(requestAllEntityTypes());
      dispatch(requestAllPropertyNames());
    },
    onClick: (entityTypeName) => dispatch(requestEntityType(entityTypeName)),
  };
};

const EntityTypesManagementContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EntityTypesManagement);

export default EntityTypesManagementContainer;
