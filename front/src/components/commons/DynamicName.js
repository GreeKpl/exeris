import React from "react";

class DynamicName extends React.Component {
  render() {
    return <span onClick={this.props.onClick}>
      {this.props.name}
      </span>;
  }
}

export default DynamicName;
