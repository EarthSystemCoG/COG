%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% advect - Solve the advection equation
%
% N      - Number of grid cells in [0,1]
% test   - Test case (1 = Sine, 2 = Gaussian, 3 = Window)
% cfl    - CFL number
% TFinal - Final time
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function advect(N, test, cfl, TFinal)

% Number of ghost cells on each side of the domain
NGhost = 1;

% Total number of cells
NTotal = N + 2 * NGhost;

% Grid spacing
dx = 1.0 / N;

% Timestep
dt = cfl * dx;

% Number of timesteps
NT = floor(TFinal / dt + 1);

% Element edge locations
XEdge = [-NGhost:(N+NGhost)+1]*dx;

% Element center locations
XCenter = 0.5 * (XEdge(2:NTotal+1) + XEdge(1:NTotal));

% Data storage
Psi = zeros(NTotal,2);

% Initialize data
for i = 1:NTotal
    if (test == 1)
        Psi(i,:) = SineFn(XCenter(i));
    elseif (test == 2)
        Psi(i,:) = GaussianFn(XCenter(i));
    elseif (test == 3)
        Psi(i,:) = WindowFn(XCenter(i));
    else
        error('Invalid test case');
    end
end

% Initialize the time
TNow = 0;

% Loop
for t = 1:NT

    % Take a small final timestep, if needed
    if (t == NT)
        dt = max(TFinal - TNow, 0);
        cfl = dt / dx;
    end

    % Update the current time
    TNow = TNow + dt;

    % Set periodic boundary conditions
    Psi(1:NGhost,:) = Psi(N+1:N+NGhost,:);
    Psi(N+NGhost+1:NTotal,:) = Psi(NGhost+1:2*NGhost,:);

    % Upwind scheme
    Psi(NGhost+1:N+NGhost, 1) = cfl * Psi(NGhost:N+NGhost-1, 1) + (1 - cfl) * Psi(NGhost+1:N+NGhost, 1);
        
    % Lax-Wendroff scheme 
    Psi(NGhost+1:N+NGhost, 2) = Psi(NGhost+1:N+NGhost, 2) ...
        - cfl / 2 * (Psi(NGhost+2:N+NGhost+1, 2) - Psi(NGhost:N+NGhost-1, 2)) ...
        + cfl^2 / 2 * (Psi(NGhost+2:N+NGhost+1, 2) - 2 * Psi(NGhost+1:N+NGhost, 2) + Psi(NGhost:N+NGhost-1, 2));

    % Exact scheme
    PsiExact = zeros(size(Psi,1),1);
    for i = 1:NTotal
        XAdj = mod(XCenter(i) - TNow,1.0);
        if (test == 1)
            PsiExact(i) = SineFn(XAdj);
        elseif (test == 2)
            PsiExact(i) = GaussianFn(XAdj);
        elseif (test == 3)
            PsiExact(i) = WindowFn(XAdj);
        end
    end
end

% Plot
plot(XCenter, Psi(:,1), '.b-', 'LineWidth', 2);
set(gca, 'FontSize', 16, 'FontWeight', 'bold');
title('Advection schemes: Upwind and Lax-Wendroff');
hold on;
plot(XCenter, Psi(:,2), '.r--', 'LineWidth', 2);
plot(XCenter, PsiExact, 'ok-', 'LineWidth', 1);
hold off;
legend({'Upwind', 'Lax-Wendroff', 'Exact'});
axis([0 1 -0.1 1.1]);
drawnow;

% Calculate error norms
for scheme = 1:2
    PsiInt = Psi(NGhost+1:N+NGhost,:);
    PsiExactInt = PsiExact(NGhost+1:N+NGhost,:);
    
    L1   = sum(abs(PsiInt(:,scheme) - PsiExactInt)) / N;
    L2   = sqrt(sum(abs(PsiInt(:,scheme) - PsiExactInt).^2) / N);
    Linf = max(abs(PsiInt(:,scheme) - PsiExactInt));
    
    disp(sprintf('\nScheme %i has error norms:', scheme));
    disp(sprintf('\tL1  : %f', L1));
    disp(sprintf('\tL2  : %f', L2));
    disp(sprintf('\tLinf: %f', Linf));
end

end

% Sine function
function y = SineFn(x)
    y = 0.5 * (1 + sin(10*pi*x));
end

% Gaussian
function y = GaussianFn(x)
    y = exp(-(x - 0.5)^2 / 0.01);
end

% Window function
function y = WindowFn(x)
    if ((x > 0.4) && (x < 0.6))
        y = 1.0;
    else
        y = 0.0;
    end
end

