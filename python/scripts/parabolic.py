#!/usr/bin/env python

import numpy as np

from pymor.core.exceptions import ExtensionError

from dune.pylrbms.artificial_channels_problem import init_grid_and_problem
from dune.pylrbms.discretize_parabolic_block_swipdg import discretize
from dune.pylrbms.estimators import ParabolicLRBMSReductor

from pymor.core.logger import set_log_levels
set_log_levels({'discretize_elliptic_block_swipdg': 'INFO',
                'lrbms': 'INFO',
                'pymor.algorithms.gram_schmidt': 'WARN'})


config = {'num_subdomains': [8, 8],
          'half_num_fine_elements_per_subdomain_and_dim': 2,
          'grid_type': 'alu'}


grid_and_problem_data = init_grid_and_problem(config)
grid = grid_and_problem_data['grid']

# d, _ = discretize(grid_and_problem_data, 1, 100)
# for mu in d.parameter_space.sample_uniformly(2):
#     U = d.solve(mu)
#     d.visualize(U, filename='mu_{}'.format(mu['switch'][0]))

d, d_data = discretize(grid_and_problem_data, 1, 100)
block_space = d_data['block_space']


# mu = d.parse_parameter([1, 1., 1., 1.])

# for i, mu in enumerate(d.parameter_space.sample_randomly(10)):
#     U = d.solve(mu)
#     d.visualize(U, filename='solution_{}'.format(i))


reductor = ParabolicLRBMSReductor(d,
                                  products=[d.operators['local_energy_dg_product_{}'.format(ii)]
                                            for ii in range(block_space.num_blocks)],
                                  num_cpus=2)


mu = d.parameter_space.sample_randomly(1)[0]
# mu = d.parse_parameter(1.)
U = d.solve(mu)
reductor.extend_basis(U)
rd = reductor.reduce()

u = rd.solve(mu)
UU = reductor.reconstruct(u)
# d.visualize(U, filename='full')
# d.visualize(UU, filename='red')
# d.visualize(U - UU, filename='error')

# B = d.solution_space.empty()
# for i in range(rd.solution_space.dim):
#     u = np.zeros(rd.solution_space.dim)
#     u[i] = 1.
#     u = rd.solution_space.from_data(u)
#     B.append(reductor.reconstruct(u))
# d.visualize(B, filename='basis')


print('Relative model reduction errors:')
print((U - UU).l2_norm() / U.l2_norm())
print()

print('Estimated error FOM:')
est, (local_eta_nc, local_eta_r, local_eta_df, time_resiudal, time_deriv_nc) = d.estimate(U, mu)
print('  total estimate:                    {}'.format(est))
print('  elliptic nonconformity indicator:  {}'.format(np.linalg.norm(local_eta_nc)))
print('  elliptic residual indicator:       {}'.format(np.linalg.norm(local_eta_r)))
print('  elliptic diffusive flux indicator: {}'.format(np.linalg.norm(local_eta_df)))
print('  time stepping residual:            {}'.format(np.linalg.norm(time_resiudal)))
print('  time derivative nonconformity:     {}'.format(np.linalg.norm(time_deriv_nc)))
print()

print('Estimated error ROM:')
est, (local_eta_nc, local_eta_r, local_eta_df, time_resiudal, time_deriv_nc) = rd.estimate(u, mu)
print('  total estimate:                    {}'.format(est))
print('  elliptic nonconformity indicator:  {}'.format(np.linalg.norm(local_eta_nc)))
print('  elliptic residual indicator:       {}'.format(np.linalg.norm(local_eta_r)))
print('  elliptic diffusive flux indicator: {}'.format(np.linalg.norm(local_eta_df)))
print('  time stepping residual:            {}'.format(np.linalg.norm(time_resiudal)))
print('  time derivative nonconformity:     {}'.format(np.linalg.norm(time_deriv_nc)))
# print(rd.mass)

# u = rd.solve(mu)
