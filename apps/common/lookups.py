from django.db.models import Lookup
from django.contrib.postgres.fields import DateTimeRangeField
from psycopg2.extras import NumericRange

@DateTimeRangeField.register_lookup
class Duration(Lookup):
  lookup_name = 'duration'

  def as_sql(self, compiler, connection):
    lhs, lhs_params = self.process_lhs(compiler, connection)
    rhs, rhs_params = self.process_rhs(compiler, connection)
    params = lhs_params + rhs_params

    if type(rhs_params[0]) is NumericRange:
        params = lhs_params + [rhs_params[0].lower] + lhs_params + [rhs_params[0].upper]
        return "duration(%s) >= (%s || ' second')::interval AND duration(%s) < (%s || ' second')::interval" % \
               (lhs, rhs, lhs, rhs), params

    return "duration(%s) = (%s || ' second')::interval" % (lhs, rhs), params


@DateTimeRangeField.register_lookup
class Matches(Lookup):
  lookup_name = 'matches'

  def as_sql(self, compiler, connection):
    lhs, lhs_params = self.process_lhs(compiler, connection)
    rhs, rhs_params = self.process_rhs(compiler, connection)
    params = lhs_params + rhs_params
    return "mod(cast(extract(epoch from lower(%s)) as int), %s)=0" % (lhs, rhs), params
