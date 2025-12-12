import pytest
import click
from epic_events.views import ContractView


def test_list_contracts_empty(capsys):
    """Test that list_contracts prints a message when no contracts exist."""
    ContractView.list_contracts([])

    output = capsys.readouterr().out
    assert "No contracts found in the database." in output


def test_list_contracts_with_contract(capsys, test_contract, test_client, test_user):
    """Test that list_contracts prints all contract information correctly."""

    ContractView.list_contracts([test_contract])

    output = capsys.readouterr().out

    assert "=== List of Contracts ===" in output
    assert str(test_contract.contract_id) in output
    assert f"{test_client.first_name} {test_client.last_name}" in output
    assert f"{test_user.first_name} {test_user.last_name}" in output
    assert str(test_contract.total_price) in output
    assert str(test_contract.rest_to_pay) in output
    assert ("Yes" if test_contract.signed else "No") in output

    assert test_contract.creation.strftime("%Y-%m-%d") in output


def test_prompt_contract_creation_full(monkeypatch):
    """Test full contract creation workflow with all fields filled."""

    answers = iter([
        1000.0,  # total_price
        600.0,  # rest_to_pay
        5,  # client_id
        3  # commercial_contact_id
    ])

    monkeypatch.setattr(
        "click.prompt",
        lambda msg, **kwargs: next(answers)
    )

    monkeypatch.setattr(
        "click.confirm",
        lambda msg, default=False: True
    )

    result = ContractView.prompt_contract_creation()

    assert result == {
        "total_price": 1000.0,
        "rest_to_pay": 600.0,
        "client_id": 5,
        "commercial_contact_id": 3,
        "signed": True
    }


def test_prompt_contract_creation_unsigned(monkeypatch):
    """Test that signed=False is returned when user declines confirmation."""

    answers = iter([
        1200.0,  # total_price
        200.0,  # rest_to_pay
        10,  # client_id
        4  # commercial_contact_id
    ])

    monkeypatch.setattr("click.prompt", lambda *a, **kw: next(answers))
    monkeypatch.setattr("click.confirm", lambda msg, default=False: False)

    result = ContractView.prompt_contract_creation()

    assert result["signed"] is False


def test_prompt_contract_creation_abort(monkeypatch):
    """Test that Click's Abort exception is properly propagated."""

    monkeypatch.setattr(
        "click.prompt",
        lambda *args, **kwargs: (_ for _ in ()).throw(click.Abort())
    )

    with pytest.raises(click.Abort):
        ContractView.prompt_contract_creation()


def test_prompt_update_no_changes(monkeypatch, test_contract):
    contract = test_contract

    answers = iter([
        contract.total_price,
        contract.rest_to_pay,
        contract.client_id,
        contract.commercial_contact_id,
    ])

    monkeypatch.setattr("click.prompt", lambda *a, **kw: next(answers))
    monkeypatch.setattr("click.confirm", lambda *a, **kw: contract.signed)

    result = ContractView.prompt_update(contract)

    assert result == {}  # Nothing changed


def test_prompt_update_some_changes(monkeypatch, test_contract):
    contract = test_contract

    answers = iter([
        1500.0,  # changed total_price
        contract.rest_to_pay,  # unchanged
        contract.client_id,  # unchanged
        contract.commercial_contact_id,  # unchanged
    ])

    monkeypatch.setattr("click.prompt", lambda *a, **kw: next(answers))
    monkeypatch.setattr("click.confirm", lambda *a, **kw: True)  # changed

    result = ContractView.prompt_update(contract)

    assert result == {
        "total_price": 1500.0,
        "signed": True
    }


def test_prompt_update_abort(monkeypatch, test_contract):
    monkeypatch.setattr(
        "click.prompt",
        lambda *a, **kw: (_ for _ in ()).throw(click.Abort())
    )

    with pytest.raises(click.Abort):
        ContractView.prompt_update(test_contract)
